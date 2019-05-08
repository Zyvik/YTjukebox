 var btn_disconnect = document.getElementById('btn_disconnect');
      var Status = document.getElementById('Status');
      // This code loads the IFrame Player API code asynchronously.
      var tag = document.createElement('script');

      tag.src = "https://www.youtube.com/iframe_api";
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      // This function creates an <iframe> (and YouTube player)
      //    after the API code downloads.
      var player;
      function onYouTubeIframeAPIReady() {
        player = new YT.Player('player', {
          height: '360',
          width: '640',
          videoId: '',
          playerVars: {
            'origin': 'http://127.0.0.1:8000',
            'loop': 1,
            'autoplay': 1
          },

          events: {
            'onReady': onPlayerReady
          }
        });
      }

      // The API will call this function when the video player is ready.
      function onPlayerReady(event) {
        var room_slug = window.location.pathname;
        room_slug = room_slug.split('/listen/')[1];
        var video = 'dummy_ID'
        var play_pause = 0;  // play pause commands counter
        var rewind = 0;  // rewind command counter
        syncState();
        maslo = setInterval(syncState,15000);

        function syncState(){
          // gets and parses JSON
          var Httpreq = new XMLHttpRequest();
          Httpreq.open("GET",'http://127.0.0.1:8000/Jukebox/api/' + room_slug);
          Httpreq.onload = function(){
            var json = JSON.parse(Httpreq.responseText);
            if (json.video != video ){
              video = json.video;
              player.loadPlaylist([video]);
              player.setLoop(true);
            }
            // Checks if there are new sweet commands for video pausing.
            if (true){
              if (json.paused){
                event.target.pauseVideo();
                Status.innerHTML = 'PAUSED';
              }
              else{
                event.target.playVideo();
                Status.innerHTML = 'PLAYING';
              }
              play_pause = json.play_pause_count;
            }

            // Checks if there are new commands for video forwarding.
            if (json.rewind_count > rewind){
              player.seekTo(json.time, true);
              rewind = json.rewind_count;
              console.log('no dziala');
            }

        };
        Httpreq.send();
        }
      }
      btn_disconnect.addEventListener("click", function(){
        clearInterval(maslo);
        btn_disconnect.disabled = true;
        btn_disconnect.innerHTML = 'Disconnected';
        Status.innerHTML = 'DISCONNECTED';
        document.getElementById('Disconnected').innerHTML = 'You are now disconnected - to reconnect refresh the page.';
      });
