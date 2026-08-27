/* TNC landing pages — custom pitch-video player.
   Native <video controls> always exposes the timeline/duration; this custom bar
   hides length entirely (play/pause, mute, captions, fullscreen only).
   Captions button auto-appears only when a caption track with cues is present. */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.pitch-player').forEach(function (p) {
    var v       = p.querySelector('video');
    var poster  = p.querySelector('.pitch-poster');
    var playBtn = p.querySelector('.pp-play');
    var muteBtn = p.querySelector('.pp-mute');
    var ccBtn   = p.querySelector('.pp-cc');
    var fsBtn   = p.querySelector('.pp-fs');
    if (!v) return;

    function play()  { v.play(); }
    poster.addEventListener('click', play);
    poster.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); }
    });
    if (playBtn) playBtn.addEventListener('click', function () { v.paused ? v.play() : v.pause(); });
    v.addEventListener('play',  function () { p.classList.add('playing'); poster.style.display = 'none'; });
    v.addEventListener('pause', function () { p.classList.remove('playing'); });
    v.addEventListener('ended', function () { p.classList.remove('playing'); poster.style.display = ''; });

    if (muteBtn) muteBtn.addEventListener('click', function () {
      v.muted = !v.muted;
      muteBtn.classList.toggle('muted', v.muted);
    });

    if (fsBtn) fsBtn.addEventListener('click', function () {
      if (document.fullscreenElement) { document.exitFullscreen(); }
      else { (p.requestFullscreen || p.webkitRequestFullscreen || function () {}).call(p); }
    });

    // Captions: only surface the CC button when a track actually has cues.
    function initCC() {
      var tt = v.textTracks && v.textTracks[0];
      if (!tt || !ccBtn) return;
      tt.mode = 'hidden';
      if (tt.cues && tt.cues.length > 0 && ccBtn.hidden) {
        ccBtn.hidden = false;
        ccBtn.addEventListener('click', function () {
          tt.mode = (tt.mode === 'showing') ? 'hidden' : 'showing';
          ccBtn.classList.toggle('on', tt.mode === 'showing');
        });
      }
    }
    var tr = v.querySelector('track');
    if (tr) tr.addEventListener('load', initCC);
    setTimeout(initCC, 1000);
  });
});
