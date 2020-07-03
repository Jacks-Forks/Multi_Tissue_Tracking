function getPostCount() {
  var post_count = document.getElementById("numPosts").value
  var video_id = document.getElementById("videoId").value
  initDraw(document.getElementById('canvas'), post_count, video_id);
}


function initDraw(canvas, post_count, video_id) {
  var boxes = []
  //  var boxCordinates = new List()


  function setMousePosition(e) {
    var ev = e || window.event; //Moz || IE
    if (ev.pageX) { //Moz
      mouse.x = ev.pageX + window.pageXOffset;
      mouse.y = ev.pageY + window.pageYOffset;
    } else if (ev.clientX) { //IE
      mouse.x = ev.clientX + document.body.scrollLeft;
      mouse.y = ev.clientY + document.body.scrollTop;
    }
  }


  var mouse = {
    x: 0,
    y: 0,
    startX: 0,
    startY: 0
  };
  var element = null;

  canvas.onmousemove = function(e) {
    setMousePosition(e);
    if (element !== null) {
      element.style.width = Math.abs(mouse.x - mouse.startX) + 'px';
      element.style.height = Math.abs(mouse.y - mouse.startY) + 'px';
      element.style.left = (mouse.x - mouse.startX < 0) ? mouse.x + 'px' : mouse.startX + 'px';
      element.style.top = (mouse.y - mouse.startY < 0) ? mouse.y + 'px' : mouse.startY + 'px';
    }
  }


  canvas.onclick = function(e) {
    if (element !== null) {
      element = null;
      canvas.style.cursor = "default";
      post_count--;
      console.log("finsihed." + post_count);
      boxes.push(GetCoordinates());
      console.log(GetCoordinates());
      if (post_count == 0) {
        console.log("stop here");
        console.log(boxes);

        var boxes_as_json = JSON.stringify(boxes);
        console.log(boxes_as_json)
        var video_id_json = JSON.stringify(video_id);
        console.log(video_id)

        const boxes_and_id = {
          boxes,
          video_id
        }
        boxes_id_asJson = JSON.stringify(boxes_and_id);
        console.log(boxes_id_asJson);

        $.ajax({
          type: 'POST',
          url: "/boxCoordinates",
          data: boxes_id_asJson,
          processData: false,
          contentType: false,
          success: function(response) {
            console.log(response);
            console.log(response.data)
            boxCoords = response.data
            $('#container').html(boxCoords.toString());
          }
        })
      }

    } else {
      console.log("begun.");
      mouse.startX = mouse.x;
      mouse.startY = mouse.y;
      element = document.createElement('div');
      element.className = 'rectangle';
      element.style.left = mouse.x + 'px';
      element.style.top = mouse.y + 'px';
      canvas.appendChild(element);
      canvas.style.cursor = "crosshair";
      boxes.push(GetCoordinates());
      console.log(GetCoordinates());
    }
  }
}


function FindPosition(oElement) {
  if (typeof(oElement.offsetParent) != "undefined") {
    for (var posX = 0, posY = 0; oElement; oElement = oElement.offsetParent) {
      posX += oElement.offsetLeft;
      posY += oElement.offsetTop;
    }
    return [posX, posY];
  } else {
    return [oElement.x, oElement.y];
  }
}


function GetCoordinates(e) {
  var PosX = 0,
    PosY = 0,
    ImgPos;
  ImgPos = FindPosition(canvas);
  if (!e) var e = window.event;
  if (e.pageX || e.pageY) {
    PosX = e.pageX;
    PosY = e.pageY;
  } else if (e.clientX || e.clientY) {
    PosX = e.clientX + document.body.scrollLeft +
      document.documentElement.scrollLeft;
    PosY = e.clientY + document.body.scrollTop +
      document.documentElement.scrollTop;
  }
  PosX = PosX - ImgPos[0];
  PosY = PosY - ImgPos[1];
  return [PosX, PosY]
}