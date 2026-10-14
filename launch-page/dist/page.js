// Progressive enhancement: screenshots remain ordinary image links without JavaScript.
const viewer = document.querySelector('#image-viewer');
const viewerImage = document.querySelector('#viewer-image');
const viewerCaption = document.querySelector('#viewer-caption');
if (viewer && typeof viewer.showModal === 'function') {
  document.querySelectorAll('[data-shot]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      const shot = link.querySelector('img');
      viewerImage.src = link.getAttribute('href');
      viewerImage.alt = shot.alt;
      viewerCaption.textContent = link.closest('figure').querySelector('figcaption').innerText.replace(/\s*\n\s*/g, ' · ');
      viewer.showModal();
    });
  });
  viewer.addEventListener('click', event => {
    if (event.target !== viewer) return;
    const bounds = viewer.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) viewer.close();
  });
}
