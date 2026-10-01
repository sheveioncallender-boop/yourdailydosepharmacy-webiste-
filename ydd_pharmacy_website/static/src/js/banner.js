/** @odoo-module **/
import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

// Scoped to the marketing banner: never binds to Odoo's header, products or cart.
export class YddBanner extends Interaction {
    static selector = ".ydd-content .banner-slider";
    setup() {
        this.slides = [...this.el.querySelectorAll(".banner-slide")];
        this.dots = [...this.el.querySelectorAll(".slide-dots button")];
        this.pauseButton = this.el.querySelector(".slide-pause");
        this.current = Math.max(0, this.slides.findIndex(el => el.classList.contains("active")));
        this.paused = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        this.hovered = false;
        this.focused = false;
        this.timer = null;
        this.touchX = null;
    }
    start() {
        if (this.slides.length < 2 || !this.pauseButton) return;
        const listen = (target, event, callback, options) => {
            if (!target) return;
            target.addEventListener(event, callback, options);
            this.registerCleanup(() => target.removeEventListener(event, callback, options));
        };
        listen(this.el.querySelector(".slide-next"), "click", () => this.move(1));
        listen(this.el.querySelector(".slide-prev"), "click", () => this.move(-1));
        this.dots.forEach((dot, index) => listen(dot, "click", () => { this.show(index); this.schedule(); }));
        listen(this.pauseButton, "click", () => { this.paused = !this.paused; this.updatePause(); });
        listen(this.el, "mouseenter", () => { this.hovered = true; this.schedule(); });
        listen(this.el, "mouseleave", () => { this.hovered = false; this.schedule(); });
        listen(this.el, "focusin", () => { this.focused = true; this.schedule(); });
        listen(this.el, "focusout", event => { if (!this.el.contains(event.relatedTarget)) { this.focused = false; this.schedule(); } });
        listen(this.el, "touchstart", event => { this.touchX = event.changedTouches[0].clientX; }, { passive: true });
        listen(this.el, "touchend", event => {
            if (this.touchX !== null) {
                const delta = event.changedTouches[0].clientX - this.touchX;
                if (Math.abs(delta) > 55) this.move(delta < 0 ? 1 : -1);
                this.touchX = null;
            }
        }, { passive: true });
        listen(document, "visibilitychange", () => this.schedule());
        this.registerCleanup(() => window.clearInterval(this.timer));
        this.show(this.current);
        this.updatePause();
    }
    show(index) {
        this.current = (index + this.slides.length) % this.slides.length;
        this.slides.forEach((slide, i) => {
            const active = i === this.current;
            slide.classList.toggle("active", active);
            slide.setAttribute("aria-hidden", String(!active));
            slide.inert = !active;
            if (this.dots[i]) {
                this.dots[i].classList.toggle("selected", active);
                this.dots[i].setAttribute("aria-pressed", String(active));
            }
        });
    }
    move(delta) { this.show(this.current + delta); this.schedule(); }
    updatePause() {
        this.pauseButton.textContent = this.paused ? "▶" : "Ⅱ";
        this.pauseButton.setAttribute("aria-label", this.paused ? "Play banners" : "Pause banners");
        this.schedule();
    }
    schedule() {
        window.clearInterval(this.timer);
        if (!this.paused && !this.hovered && !this.focused && !document.hidden) {
            this.timer = window.setInterval(() => this.show(this.current + 1), 7500);
        }
    }
}
registry.category("public.interactions").add("ydd_pharmacy_website.banner", YddBanner);
