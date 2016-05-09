/**
 * Created by Firdaus on 4/25/2016.
 */
      var socket = io();
      $('form').on('submit',function(event){
        event.preventDefault();

        var msg  = $('#m').val();
        console.log( msg);
        socket.send(msg);

        $('#m').val('');
        return false;
      });
      $('#leave').on('click',function(event){
          event.preventDefault();
          socket.emit("leave")
      });
      socket.on('message', function(msg){
        $('#messages').append($('<li>').text(msg));
      });
      socket.on('users', function(msg){
        $('#users').append($('<li>').text(msg));
      });
