(function () {
    "use strict";

    var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function ready(fn) {
        if (document.readyState !== "loading") {
            fn();
        } else {
            document.addEventListener("DOMContentLoaded", fn, { once: true });
        }
    }

    ready(function () {
        document.body.classList.add("nddl-page-ready");

        var updateScrollState = function () {
            document.body.classList.toggle("nddl-scrolled", window.scrollY > 12);
        };
        updateScrollState();
        window.addEventListener("scroll", updateScrollState, { passive: true });

        if (!prefersReducedMotion && "IntersectionObserver" in window) {
            var revealTargets = document.querySelectorAll(
                ".title-area, .property-card2, .property-card4, .project-card, .img-box, .wpforms-container, .contact-info, .wperf-card, .footer-wrap"
            );
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });

            revealTargets.forEach(function (element, index) {
                element.classList.add("nddl-reveal");
                element.style.transitionDelay = Math.min(index % 6, 5) * 55 + "ms";
                observer.observe(element);
            });
        }

        if (!prefersReducedMotion && window.matchMedia("(hover: hover)").matches) {
            document.querySelectorAll(".property-card2, .property-card4, .project-card").forEach(function (card) {
                card.addEventListener("pointermove", function (event) {
                    var rect = card.getBoundingClientRect();
                    var x = ((event.clientX - rect.left) / rect.width - 0.5) * 7;
                    var y = ((event.clientY - rect.top) / rect.height - 0.5) * -7;
                    card.style.setProperty("--tilt-x", x.toFixed(2) + "deg");
                    card.style.setProperty("--tilt-y", y.toFixed(2) + "deg");
                    card.classList.add("nddl-tilt");
                });
                card.addEventListener("pointerleave", function () {
                    card.classList.remove("nddl-tilt");
                    card.style.removeProperty("--tilt-x");
                    card.style.removeProperty("--tilt-y");
                });
            });
        }

        document.querySelectorAll('a[href]:not([target]):not([href^="#"]):not([href^="tel:"]):not([href^="mailto:"])').forEach(function (link) {
            link.addEventListener("click", function (event) {
                var url = new URL(link.href, window.location.href);
                if (url.origin !== window.location.origin || prefersReducedMotion || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
                    return;
                }
                document.body.classList.add("nddl-page-leaving");
            });
        });
    });
})();
