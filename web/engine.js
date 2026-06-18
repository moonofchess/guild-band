export class GameEngine {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.sprites = [];
        this.vfxs = [];
        this.texts = []; // Floating combat text
        this.lastTime = 0;
        this.isCombat = false;
        
        // Background image
        this.bgImage = new Image();
    }

    setBattleBackground(src) {
        this.bgImage.src = src;
    }

    clear() {
        this.sprites = [];
        this.vfxs = [];
        this.texts = [];
        this.isCombat = false;
    }

    spawnSprite(src, x, y, scale, isEnemy, mercData = null) {
        const sprite = new CombatSprite(src, x, y, scale, isEnemy, mercData);
        this.sprites.push(sprite);
        return sprite;
    }

    spawnVfx(src, x, y, size, totalFrames, duration = 500, type = 'static') {
        const vfx = new VfxEffect(src, x, y, size, totalFrames, duration, type);
        this.vfxs.push(vfx);
        return vfx;
    }

    spawnProjectile(src, startX, startY, endX, endY, size, totalFrames, speed = 0.5, onImpact = null) {
        const proj = new ProjectileVfx(src, startX, startY, endX, endY, size, totalFrames, speed, onImpact);
        this.vfxs.push(proj);
    }

    spawnFloatingText(text, x, y, color = '#ff5252') {
        this.texts.push({
            text: text,
            x: x,
            y: y,
            oy: 0,
            alpha: 1.0,
            color: color
        });
    }

    update(dt) {
        if (this.isCombat) {
            this.sprites.forEach(s => s.update(dt));
            
            // Update VFX
            this.vfxs = this.vfxs.filter(v => {
                v.update(dt);
                return !v.isFinished;
            });

            // Update texts
            this.texts.forEach(t => {
                t.oy -= 0.05 * dt; // drift up
                t.alpha -= 0.0015 * dt; // fade out
            });
            this.texts = this.texts.filter(t => t.alpha > 0);
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw battle background if loaded
        if (this.isCombat && this.bgImage.complete && this.bgImage.src) {
            this.ctx.drawImage(this.bgImage, 0, 0, this.canvas.width, this.canvas.height);
        }

        if (this.isCombat) {
            // Sort sprites by Y so bottom is drawn on top
            const sorted = [...this.sprites].sort((a, b) => a.y - b.y);
            sorted.forEach(s => s.draw(this.ctx));
            
            // Draw VFX
            this.vfxs.forEach(v => v.draw(this.ctx));

            // Draw floating text
            this.ctx.save();
            this.texts.forEach(t => {
                this.ctx.globalAlpha = Math.max(0, t.alpha);
                this.ctx.font = 'bold 24px Arial';
                this.ctx.fillStyle = t.color;
                this.ctx.strokeStyle = '#000000';
                this.ctx.lineWidth = 4;
                this.ctx.strokeText(t.text, t.x, t.y + t.oy);
                this.ctx.fillText(t.text, t.x, t.y + t.oy);
            });
            this.ctx.restore();
        }
    }

    loop(timestamp = 0) {
        const dt = timestamp - this.lastTime;
        this.lastTime = timestamp;
        
        this.update(dt);
        this.draw();
        
        requestAnimationFrame(this.loop.bind(this));
    }
}

// 5-row Animation Sprite Sheet handler
class CombatSprite {
    constructor(src, x, y, scale, isEnemy, data = null) {
        this.image = new Image();
        this.image.src = src;
        this.x = x;
        this.y = y;
        this.scale = scale;
        this.isEnemy = isEnemy;
        this.data = data; // Reference to Mercenary or Monster data
        
        this.currentAnim = "idle";
        this.currentFrame = 0;
        this.frameTime = 0;
        this.fps = 8;
        
        // Grid setup defaults (will recalculate on image load)
        this.cols = 4; // default frames per row
        this.rows = 5; // idle, move, attack, hit, death
        
        this.image.onload = () => {
            this.frameWidth = this.image.width / this.cols;
            this.frameHeight = this.image.height / this.rows;
        };

        // UI states
        this.isSelected = false;
        this.shakeTimer = 0;
    }

    setAnimation(name) {
        if (this.currentAnim === name && name !== "attack") return;
        this.currentAnim = name;
        this.currentFrame = 0;
        this.frameTime = 0;

        // Custom configs
        if (name === "hit") this.fps = 10;
        else if (name === "attack") this.fps = 12;
        else this.fps = 8;
    }

    update(dt) {
        this.frameTime += dt;
        let framesInRow = 4;
        if (this.currentAnim === "hit") framesInRow = 2;
        if (this.currentAnim === "attack") framesInRow = 4; // or 6 depending on sheet

        if (this.frameTime > 1000 / this.fps) {
            this.currentFrame++;
            if (this.currentFrame >= framesInRow) {
                if (this.currentAnim === "attack" || this.currentAnim === "hit") {
                    this.setAnimation("idle"); // revert to idle
                } else if (this.currentAnim === "death") {
                    this.currentFrame = framesInRow - 1; // stay on last frame
                } else {
                    this.currentFrame = 0;
                }
            }
            this.frameTime = 0;
        }

        if (this.shakeTimer > 0) {
            this.shakeTimer -= dt;
        }
    }

    draw(ctx) {
        if (!this.frameWidth) return;

        let rowIdx = 0;
        switch (this.currentAnim) {
            case "idle": rowIdx = 0; break;
            case "move": rowIdx = 1; break;
            case "attack": rowIdx = 2; break;
            case "hit": rowIdx = 3; break;
            case "death": rowIdx = 4; break;
        }

        ctx.save();
        
        // Shake logic
        let offsetX = 0;
        if (this.shakeTimer > 0) {
            offsetX = (Math.random() - 0.5) * 10;
        }

        ctx.translate(this.x + offsetX, this.y);
        
        // Flip enemies
        if (this.isEnemy) {
            ctx.scale(-1, 1);
        }

        const s = Math.abs(this.scale);
        ctx.drawImage(
            this.image,
            this.currentFrame * this.frameWidth, rowIdx * this.frameHeight, this.frameWidth, this.frameHeight,
            -(this.frameWidth * s) / 2, -(this.frameHeight * s) / 2, this.frameWidth * s, this.frameHeight * s
        );

        ctx.restore();

        // Draw HUD (HP/MP bars, Name, Selection cursor) above characters if alive
        if (this.data && this.data.hp > 0) {
            this.drawHUD(ctx);
        }
    }

    drawHUD(ctx) {
        const s = Math.abs(this.scale);
        const hudY = this.y - (this.frameHeight * s) / 2 - 10;
        const hudW = 60;
        const hudX = this.x - hudW / 2;

        // Draw Selection cursor pointing down
        if (this.isSelected) {
            ctx.save();
            const bounce = Math.sin(Date.now() / 150) * 5;
            ctx.fillStyle = '#ff3333';
            ctx.beginPath();
            ctx.moveTo(this.x, hudY - 15 + bounce);
            ctx.lineTo(this.x - 6, hudY - 25 + bounce);
            ctx.lineTo(this.x + 6, hudY - 25 + bounce);
            ctx.closePath();
            ctx.fill();
            ctx.restore();
        }

        // Draw HP Bar
        const hpPct = Math.max(0, this.data.hp / this.data.maxHp);
        ctx.fillStyle = '#222';
        ctx.fillRect(hudX, hudY, hudW, 5);
        ctx.fillStyle = '#ff4444';
        ctx.fillRect(hudX, hudY, hudW * hpPct, 5);

        // Draw MP Bar (Only for allies who have maxMp > 0)
        if (!this.isEnemy && this.data.maxMp > 0) {
            const mpPct = Math.max(0, this.data.mp / this.data.maxMp);
            ctx.fillStyle = '#222';
            ctx.fillRect(hudX, hudY + 7, hudW, 4);
            ctx.fillStyle = '#4488ff';
            ctx.fillRect(hudX, hudY + 7, hudW * mpPct, 4);
        }

        // Draw Name text
        ctx.font = '11px sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText(this.data.name, this.x, hudY - 6);

        // Draw Status indicators (Stun, Poison, Bleed)
        let stateOffset = -22;
        if (this.data.states && this.data.states.includes("독")) {
            ctx.fillStyle = '#c0392b';
            ctx.fillRect(this.x - 18, hudY + stateOffset, 10, 10);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 8px sans-serif';
            ctx.fillText("P", this.x - 13, hudY + stateOffset + 8);
        }
        if (this.data.states && this.data.states.includes("출혈")) {
            ctx.fillStyle = '#962d2d';
            ctx.fillRect(this.x, hudY + stateOffset, 10, 10);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 8px sans-serif';
            ctx.fillText("B", this.x + 5, hudY + stateOffset + 8);
        }
        if (this.data.stunned_turns && this.data.stunned_turns > 0) {
            ctx.fillStyle = '#f1c40f';
            ctx.fillRect(this.x + 12, hudY + stateOffset, 10, 10);
            ctx.fillStyle = '#000000';
            ctx.font = 'bold 8px sans-serif';
            ctx.fillText("S", this.x + 17, hudY + stateOffset + 8);
        }
    }
}

// VFX animation player
class VfxEffect {
    constructor(src, x, y, size, totalFrames, duration, type = 'static') {
        this.image = new Image();
        this.image.src = src;
        this.x = x;
        this.y = y;
        this.size = size;
        this.totalFrames = totalFrames;
        this.duration = duration;
        this.type = type; // 'static'
        
        this.elapsed = 0;
        this.currentFrame = 0;
        this.isFinished = false;
        
        this.image.onload = () => {
            this.frameWidth = this.image.width / this.totalFrames;
            this.frameHeight = this.image.height;
        };
    }

    update(dt) {
        this.elapsed += dt;
        this.currentFrame = Math.floor((this.elapsed / this.duration) * this.totalFrames);
        if (this.currentFrame >= this.totalFrames) {
            this.isFinished = true;
            this.currentFrame = this.totalFrames - 1;
        }
    }

    draw(ctx) {
        if (!this.frameWidth || this.isFinished) return;
        
        ctx.save();
        ctx.translate(this.x, this.y);
        ctx.drawImage(
            this.image,
            this.currentFrame * this.frameWidth, 0, this.frameWidth, this.frameHeight,
            -this.size / 2, -this.size / 2, this.size, this.size
        );
        ctx.restore();
    }
}

// Flying projectile VFX
class ProjectileVfx {
    constructor(src, startX, startY, endX, endY, size, totalFrames, speed, onImpact) {
        this.image = new Image();
        this.image.src = src;
        this.x = startX;
        this.y = startY;
        this.startX = startX;
        this.startY = startY;
        this.endX = endX;
        this.endY = endY;
        this.size = size;
        this.totalFrames = totalFrames;
        this.speed = speed; // pct per millisecond
        this.onImpact = onImpact;
        
        this.progress = 0;
        this.currentFrame = 0;
        this.frameTime = 0;
        this.isFinished = false;

        this.image.onload = () => {
            this.frameWidth = this.image.width / this.totalFrames;
            this.frameHeight = this.image.height;
        };
    }

    update(dt) {
        this.progress += this.speed * dt;
        if (this.progress >= 1.0) {
            this.progress = 1.0;
            this.isFinished = true;
            if (this.onImpact) {
                this.onImpact();
            }
        }
        
        // Linearly interpolate positions
        this.x = this.startX + (this.endX - this.startX) * this.progress;
        this.y = this.startY + (this.endY - this.startY) * this.progress;

        this.frameTime += dt;
        if (this.frameTime > 80) {
            this.currentFrame = (this.currentFrame + 1) % this.totalFrames;
            this.frameTime = 0;
        }
    }

    draw(ctx) {
        if (!this.frameWidth || this.isFinished) return;

        ctx.save();
        ctx.translate(this.x, this.y);
        
        // Calculate angle of movement
        const angle = Math.atan2(this.endY - this.startY, this.endX - this.startX);
        ctx.rotate(angle);

        ctx.drawImage(
            this.image,
            this.currentFrame * this.frameWidth, 0, this.frameWidth, this.frameHeight,
            -this.size / 2, -this.size / 2, this.size, this.size
        );
        ctx.restore();
    }
}
