Let's add ML model that detects issues during printing via the printer built in camera.

I've loaded a model that should be able to do the job in src/issue_detector.py.

Update the issue_detector to open http://192.168.1.108:8080/?action=stream as input stream and each 5th second to get the latest available frame and run it for inference. Print the result in the logs.

Goals:
1) Update the issue_detector to open http://192.168.1.108:8080/?action=stream as input stream and each 5th second to get the latest available frame and run it for inference. Print the result in the logs. 
2) Extend issue detector to be a component that can be started/stopped when needed. For that we go with multiprocessing.
2) The issue detector component should run only when printing. If printer state is unknown or != printing - the component should stay idle. Update the code base to account for that.
3) 

General requirements:
 * Use the model from https://huggingface.co/Javiai/3dprintfails-yolo5vs
 * Run the model on the CPU

For all steps follow industry wide patterns and good coding practices.

Implementation plan:
1) Create a script that downloads and converts the model to OpenVINO model
2) Integrate the model into the code base. Do inferences only when printing. One inference each second.
3) Once inference information is available - send notifications via the notifier.send_notification method for any inference with score above 50 for the spaghetti/error classes. Define per class threshold in the config.



Additional details: The camera images can be retrieved from video stream on the following URL: "http://192.168.1.108:8080/?action=stream" . Keep the URL in the config. This is MJPG video stream with 640x480 resolution. Aim for efficient video processing, but don't overengineeer it. Most efficient and yet simple video processing options is what I need. Keep the video stream processing off when the printer is not printing.

After each step of the implementation plan pause, let me review and proceed with next step once I've confirmed we are good to go with it.