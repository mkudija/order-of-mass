/**
 * script.js - Main JavaScript file for Order of Mass
 * Contains logic for:
 * 1. Biblical Footnotes (popups on hover)
 * 2. Table of Contents (scroll spy and smooth scrolling)
 */

// ==========================================
// 1. Biblical Footnotes Logic
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    let bibleData = null;

    // Fetch Bible data
    fetch('bible.json')
        .then(response => response.json())
        .then(data => {
            bibleData = data;
            initFootnotes();
        })
        .catch(error => console.error('Error loading bible.json:', error));

    function initFootnotes() {
        const footnotes = document.querySelectorAll('.footnote-ref');

        footnotes.forEach(fn => {
            fn.addEventListener('mouseenter', (e) => {
                const refKey = fn.getAttribute('data-ref');
                const data = bibleData[refKey];

                if (data) {
                    showPopup(fn, data);
                }
            });

            fn.addEventListener('mouseleave', () => {
                hideAllPopups();
            });
        });
    }

    function showPopup(element, data) {
        hideAllPopups();

        const popup = document.createElement('div');
        popup.className = 'footnote-popup active';
        popup.innerHTML = `<strong>${data.ref}</strong><br>${data.text}<br><span class="nabre-tag">NABRE</span>`;

        document.body.appendChild(popup);

        // Position popup
        const rect = element.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        popup.style.top = (rect.bottom + scrollTop + 5) + 'px';
        popup.style.left = rect.left + 'px';
    }

    function hideAllPopups() {
        const popups = document.querySelectorAll('.footnote-popup');
        popups.forEach(p => p.remove());
    }
});

// ==========================================
// 2. Table of Contents Logic
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // Get all sections with IDs
    const sections = document.querySelectorAll('h1[id], h2[id], h3[id]');
    const tocLinks = document.querySelectorAll('.toc-link');

    // Create a map of href to link element
    const linkMap = new Map();
    tocLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href) {
            linkMap.set(href.substring(1), link); // Remove the # from href
        }
    });

    // Track which section is currently in view
    function highlightTOC() {
        let current = '';
        const scrollPosition = window.scrollY + 150; // Offset for better UX

        // Find the current section by checking which one we've scrolled past
        sections.forEach(section => {
            const sectionTop = section.offsetTop;

            // If we've scrolled past this section, it might be the current one
            if (scrollPosition >= sectionTop) {
                current = section.getAttribute('id');
            }
        });

        // Update active class
        tocLinks.forEach(link => {
            link.classList.remove('active');
        });

        if (current && linkMap.has(current)) {
            const activeLink = linkMap.get(current);
            activeLink.classList.add('active');

            // Scroll the active link into view within the TOC sidebar
            const toc = document.getElementById('toc');
            if (toc) {
                const linkRect = activeLink.getBoundingClientRect();
                const tocRect = toc.getBoundingClientRect();
                if (linkRect.top < tocRect.top || linkRect.bottom > tocRect.bottom) {
                    activeLink.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                }
            }
        }
    }

    // Smooth scroll for TOC links
    tocLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 20,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Throttle scroll events for better performance
    let scrollTimeout;
    window.addEventListener('scroll', function () {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }
        scrollTimeout = window.requestAnimationFrame(highlightTOC);
    });

    // Initial highlight
    highlightTOC();
});
