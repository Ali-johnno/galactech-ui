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
var submit_btn = document.getElementById("submit");
var audioUpload = document.getElementsByClassName("audio-upload")[0];
//add events to those 3 buttons 
const uploadURL = "/upload";
const dropArea = document.querySelector(".drag-and-drop"),
dragText = dropArea.querySelector("header"),
button = dropArea.querySelector("button"),
drag_input = dropArea.querySelector("input");
let file;

var drag_drop = document.getElementsByClassName("drag-and-drop")[0];
var uploaded_file = document.getElementsByClassName("uploaded-audio")[0];

button.onclick = ()=>{
    drag_input.click(); //if user click on the button then the input also clicked
}

drag_input.addEventListener("change", function(){
//getting user select file and [0] this means if user select multiple files then we'll select only the first one
file = this.files[0];
changeFileDisplay();
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
submit_btn.classList.add('drop_or_browse');
showFile(); //calling function
});


function showFile(){
let fileType = file.type; //getting selected file type
let validExtensions = ["video/ogg", "video/mp4","video/webm" ,"audio/ogg", "audio/mpeg", "audio/mp3", "audio/wav"]; 
if(validExtensions.includes(fileType)){ //if user selected file is an audio/video file
    let fileReader = new FileReader(); //creating new FileReader object
    fileReader.onload = ()=>{
    let fileURL = fileReader.result; //passing user file source in fileURL variable
        
    
    addRecording(file);
    }
    changeFileDisplay();
    document.getElementsByClassName("file-name")[0].innerHTML = file.name;
    fileReader.readAsDataURL(file);


}else{
    alert("File must be audio or video file!");
    dropArea.classList.remove("active");
    dragText.textContent = "Drag & Drop to Upload File";
}
}


function changeFileDisplay(){
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
    instructions.innerHTML = "INSTRUCTIONS: TO STOP RECORDING PRESS THE STOP BUTTON BELOW. RECORDING STOPS AFTER 2 MINUTES.";
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

	
}).catch(function(err) {
    //enable the record button if getUserMedia() fails 
   
});
}



function stopRecording() {
    console.log("stopButton clicked");
    //disable the stop button, enable the record too allow for new recordings 
    document.getElementById("stop").id = "submit";
    recordIcons.classList.remove("fas","fa-stop");
    recordIcons.classList.add("fas", "fa-check");
    instructions.innerHTML = "INSTRUCTIONS: IF YOU ARE READY TO SUBMIT PRESS THE TICK BELOW.";
    //tell the recorder to stop the recording 
    rec.stop(); //stop microphone access 
    gumStream.getAudioTracks()[0].stop();
    //create the wav blob and pass it on to createDownloadLink 
    submit_btn.classList.add('microphone');
    submit_audio.classList.remove("d-none");
    rec.exportWAV(createDownloadLink);
}

function createDownloadLink(blob) {
    addRecording(blob);
    microphone_blob = blob;
};


submit_btn.addEventListener("click", function(e){
    e.preventDefault();
    console.log("submit");
    let formData = new FormData();
    if (submit_btn.classList.contains("drop_or_browse") === true){
        console.log("drag_or_browse selected");
        formData.append("audio_file", file, "audio_file");
    } else if (submit_btn.classList.contains("microphone") === true){
        console.log("microphone audio selected");
        formData.append("audio_file", microphone_blob, "audio_file");
    }
    console.log(formData);
    $.ajax({
        type: 'POST',
        url: 'http://localhost:8080/upload',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response){
            console.log("successfully uploaded");
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