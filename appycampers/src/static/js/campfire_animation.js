// This animation script for the campfire svg was generated using ChatGPT 5.6-Sol with thinking effort set to high
(() => {
    if (typeof gsap === 'undefined') {
        console.log('failed to get gsap')
        return;
    }

    const media = gsap.matchMedia();

    media.add('(prefers-reduced-motion: no-preference)', () => {
        const timeline = gsap.timeline();

        timeline.to('.flame-back', {
            scaleX: 0.84, scaleY: 1.10, rotation: -3,
            transformOrigin: '50% 100%', duration: 0.84,
            ease: 'sine.inOut', yoyo: true, repeat: -1
        }, 0);

        timeline.to('.flame-front', {
            scaleX: 1.12, scaleY: 0.9, rotation: 3,
            transformOrigin: '50% 100%', duration: 0.65,
            ease: 'sine.inOut', yoyo: true, repeat: -1
        }, 0);

        timeline.to('.fire-glow', {
            opacity: 0.56, scale: 1.07,
            transformOrigin: '50% 50%', duration: 1.2,
            ease: 'sine.inOut', yoyo: true, repeat: -1
        }, 0);

        timeline.to('.fire-halo', {
            opacity: 0.5, scaleX: 1.16,
            transformOrigin: '50% 50%', duration: 0.97,
            ease: 'sine.inOut', yoyo: true, repeat: -1
        }, 0);

        document.querySelectorAll('.ember').forEach((ember, i) => {
            timeline.fromTo(ember,
                { opacity: 0, y: 5, x: 0 },
                {
                    opacity: 0.85,
                    y: -40 - i * 11,
                    x: i % 2 ? 9 : -9,
                    duration: 1.7 + i * 0.38,
                    ease: 'power1.out',
                    repeat: -1,
                    repeatDelay: 0.3
                },
                i * 0.32
            );
        });
    });
})();