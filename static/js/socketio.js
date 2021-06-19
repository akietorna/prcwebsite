document.addEventListener('DOMContentLoaded',() =>{
    var socket = io.connect('http://' + document.domain + ':' + location.port );
    

    let room;

    // displays message in the display-message div tag

    socket.on('message', data=>{
        const p = document.createElement('p');
        const br = document.createElement('br');
        const span_username = document.createElement('span');
        const span_timestamp = document.createElement('span')

        span_username.innerHTML= data.username;
        span_timestamp.innerHTML = data.time_stamp;

        p.innerHTML = data.msg +br.outerHTML + span_timestamp.outerHTML;
        document.querySelector('#message-sent-test').append(p);
    })

    
    

    // tacking care of the joining and leaving room 
    document.querySelector('#start-chat').forEach(p =>{   
        p.onclick = () =>{
            let newRoom = p.innerHTML;
             if (newRoom ==room){
                msg = `You are already  in the counselling room`
                printSysMsg(msg);
            } else{
                leaveRoom();
                joinRoom();
                room = newRoom;
            }
        }
    })
    


    //sending nessage

    document.querySelector('#send-message').onclick = () =>{
        socket.send({'msg': document.querySelector('#message-box').value, 'username': username});
        document.getElementById('message-box').value = "";
    }


    // leaving the room

    function leaveRoom(room){
        socket.emit('leave',{'username': username, 'room': room});
    }

    // joining the room

    function joinRoom(room){
        socket.emit('join',{'username': username, 'room': room});
    }

    //printing system messages

    function printSysMsg(msg){
        const p = document.createElement('p');
        p.innerHTML = msg;
        document.querySelector('#message-sent').append(p);


    }


    document.querySelector('#Start-chart').onclick = () =>{
        document.getElementById('start-chat').value = "Leave Chat";
    }

    

})