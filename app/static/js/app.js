URL = window.URL || window.webkitURL;
var gumStream;
//stream from getUserMedia() 
var rec;
//Recorder.js object 
var input;
//MediaStreamAudioSourceNode we'll be recording 
// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext;
//new audio context to help us record 
var recordButton = document.getElementById("mic");
var recordIcons = document.getElementsByClassName("recorder-icons")[0];
var submit_audio = document.getElementsByClassName("submit-audio")[0];
var stopButton;
var instructions = document.getElementById("instructions");
var submit_btn = document.getElementById("submit-recording");
var audioUpload = document.getElementsByClassName("audio-upload")[0];
var recording = document.getElementsByClassName("recording")[0];
var recorder = document.getElementsByClassName("recorder")[0];
var timer = document.getElementById("timer");

//add events to those 3 buttons 
const uploadURL = "/upload";
const dropArea = document.querySelector(".drag-and-drop"),
dragText = dropArea.querySelector("header"),
button = dropArea.querySelector("button"),
drag_input = dropArea.querySelector("input");
let file;
let timeout;

var drag_drop = document.getElementsByClassName("drag-and-drop")[0];
var uploaded_file = document.getElementsByClassName("uploaded-audio")[0];
var removeAudioTrigger = document.getElementById("remove-audio");
var deleteModal = document.getElementById("delete-modal");
var cancelRemoveAudio = document.getElementById("cancel-delete-btn");
var closeModal = document.getElementById("close-modal");
var removeMphAudioTrigger = document.getElementById("delete-microphone-recording");

var js_flash = document.getElementById("js-flash");


button.onclick = ()=>{
    drag_input.click(); //if user click on the button then the input also clicked
}

drag_input.addEventListener("change", function(){
//getting user select file and [0] this means if user select multiple files then we'll select only the first one
    file = this.files[0];
    showFile(); //calling function
});

dropArea.addEventListener("dragover", (event)=>{
    event.preventDefault(); //preventing from default behaviour
    dropArea.classList.add("active");
    dragText.textContent = "Release to Upload File";
});

//If user leave dragged File from DropArea
dropArea.addEventListener("dragleave", ()=>{
    dropArea.classList.remove("active");
    dragText.textContent = "Drag & Drop to Upload File";
});

//If user drop File on DropArea
dropArea.addEventListener("drop", (event)=>{
    event.preventDefault(); //preventing from default behaviour

    //getting user select file and [0] this means if user select multiple files then we'll select only the first one
    file = event.dataTransfer.files[0];
    submit_btn.classList.add('drag-or-browse');
    showFile(); //calling function
});


function showFile(){
let fileType = file.type; //getting selected file type
let validExtensions = ["video/ogg", "video/mp4","video/webm" ,"audio/ogg", "audio/mpeg", "audio/mp3", "audio/wav"]; 
let size = file.size/1024/1024;
var error_div = document.getElementById("js-error-message");

if(validExtensions.includes(fileType) &&  (size < 25)){ //if user selected file is an audio/video file
    let fileReader = new FileReader(); //creating new FileReader object
    fileReader.onload = ()=>{
    let fileURL = fileReader.result; //passing user file source in fileURL variable
    addRecording(file);
    }
    error_div.classList.add("d-none");
    changeFileDisplay();
    document.getElementsByClassName("file-name")[0].innerHTML = file.name;
    
    fileReader.readAsDataURL(file);
} else {
    
    error_div.classList.remove("d-none");
    if (size > 25){
        console.log("File size too big! File must be 25 MB or smaller");
        error_div.innerHTML = "File size too big! File must be 25 MB or smaller";
    } else {
        console.log("File must be an audio or video file!");
        error_div.innerHTML = "File must be audio or video file!"
    }
    dropArea.classList.remove("active");
    dragText.textContent = "Drag & Drop to Upload File";
}
}


function changeFileDisplay(){
    recording.classList.remove('d-none');
    recorder.classList.add('d-none');
    submit_audio.classList.remove("d-none");
    dropArea.classList.remove("active");
    dragText.textContent = "Drag & Drop to Upload File";
    recordButton.disabled = true;
    recordButton.style.display = "none";
    audioUpload.classList.add("change-display-two");
    drag_drop.classList.add("change-display");
    uploaded_file.classList.remove("d-none");
}





recordButton.addEventListener("click", startRecording);



function startRecording() { 
var constraints = {
    audio: true,
    video: false
} 
/* Disable the record button until we get a success or fail from getUserMedia() */
	document.getElementById("mic").id = "stop";
	stopButton = document.getElementById("stop");
    recordIcons.classList.remove("fas", "fa-microphone");
    recordIcons.classList.add("fas" ,"fa-stop");
	stopButton.removeEventListener("click",startRecording);
	stopButton.addEventListener("click", stopRecording);
    instructions.innerHTML = "INSTRUCTIONS: TO STOP RECORDING PRESS THE STOP BUTTON BELOW. RECORDING STOPS AFTER ONE MINUTE";
    audioUpload.style.display = "none";



/* We're using the standard promise based getUserMedia()

https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia */

audioContext.resume().then(() => {
    console.log('Playback resumed successfully');
  });
navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    console.log("getUserMedia() success, stream created, initializing Recorder.js ..."); 
    /* assign to gumStream for later use */
    gumStream = stream;
    /* use the stream */
    input = audioContext.createMediaStreamSource(stream);
    /* Create the Recorder object and configure to record mono sound (1 channel) Recording 2 channels will double the file size */
    rec = new Recorder(input, {
        numChannels: 1
    }) 
    //start the recording process 
    rec.record()
    console.log("Recording started");
    timer.classList.remove("d-none");

	timeout = setTimeout(() => {
        stopRecording()
      }, 60500);
    
    recording_timer();
    
}).catch(function(err) {
    //enable the record button if getUserMedia() fails 
   
});
}



function stopRecording() {
    console.log("stopButton clicked");
    //disable the stop button, enable the record too allow for new recordings 
    document.getElementById("stop").id = "submit";
    recordIcons.classList.remove("fas","fa-stop");
    recordIcons.classList.add("far","fa-thumbs-up");
    instructions.innerHTML = "INSTRUCTIONS: SUBMIT THE AUDIO RECORDING TO IDENTIFY THE ACCENT OR DELETE THE RECORDING TO START OVER.";
    //tell the recorder to stop the recording 
    rec.stop(); //stop microphone access 
    gumStream.getAudioTracks()[0].stop();
    //create the wav blob and pass it on to createDownloadLink 
    submit_btn.classList.add('microphone');
    timer.classList.add("d-none");
    submit_audio.classList.remove("d-none");
    recording.classList.remove("d-none");
    removeMphAudioTrigger.classList.remove("d-none");
    rec.exportWAV(createDownloadLink);
}

function createDownloadLink(blob) {
    addRecording(blob);
    microphone_blob = blob;
};


submit_btn.addEventListener("click", function(){
    console.log("submit");
    
    let formData = new FormData();
    if (submit_btn.classList.contains("drag-or-browse") === true){
        console.log("drag or browse selected");
        formData.append("audio_file", file, "audio_file");
    } else if (submit_btn.classList.contains("microphone") === true){
        console.log("microphone audio selected");
        formData.append("audio_file", microphone_blob, "audio_file");
    }
    console.log(formData);
    console.log(file);
    $.ajax({
        type: 'POST',
        url: 'http://localhost:8080/upload',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response){
            console.log("audio file sent to flask");
            window.location.href = "results";
        }
    });
});


function addRecording(url){
    var url = URL.createObjectURL(url);
    var recordingsList = document.getElementById('recordingsList');
    var au = document.createElement('audio');
    var li = document.createElement('li');
    au.controls = true;
    au.src = url;
    li.appendChild(au);
    $(recordingsList).empty();
    recordingsList.appendChild(li);
};

removeAudioTrigger.addEventListener("click", function(e){
    e.preventDefault();
    deleteModal.classList.remove("d-none");
});

removeMphAudioTrigger.addEventListener("click", function(e){
    e.preventDefault();
    deleteModal.classList.remove("d-none");
});

cancelRemoveAudio.addEventListener("click", function(e){
    e.preventDefault();
    deleteModal.classList.add("d-none");
});

closeModal.addEventListener("click", function(e){
    e.preventDefault();
    deleteModal.classList.add("d-none");
});

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

window.setTimeout(function() {
    $(".alert").fadeTo(100, 0).slideUp(100, function(){
        $(this).remove(); 
    });
}, 4000);

function recording_timer(){
    
    if (JSON.stringify(document.getElementById("submit")) != "null"){
        console.log("stop button stopped timer");
        clearInterval(timeout);
        return;
    }
    
    var time = timer.innerText.split(":");
    var min = time[0];
    var sec = time[1];

    console.log("timer started");
    if (sec == 59){
        min++;
        sec = 0;
        if (min < 10) min = "0" + min;
        document.getElementById("timer").innerHTML = "<h1>" + min + ":0" + sec + "</h1>";
        timer.classList.remove("timer-ending");
        console.log("timer ended");
        return;
    } else {
        sec ++;
    }
    if (sec < 10){
            sec = "0" + sec;
    }
    if (sec >= 45){
        if (timer.classList.contains("timer-ending") === false){
            timer.classList.add("timer-ending");
        }
    }
    

    document.getElementById("timer").innerHTML = "<h1>" + min + ":" + sec + "</h1>";
    setTimeout(recording_timer, 1000);
}