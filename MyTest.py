from torch.hub import load
# import cv2

# Model
model = load('WongKinYiu/yolov7', 'custom', 'last.pt', trust_repo=0.01)

def find_Obstacle(img):
    # Images
    # img = f'{str(i)}.png'  # or file, Path, PIL, OpenCV, numpy, list

    # Inference
    results = model(img)

    # Extract information about detected objects
    objects = results.pred[0][:, -1].tolist()  # List of detected object labels
    bounding_boxes = results.pred[0][:, :-1].cpu().numpy().tolist()  # List of bounding boxes

    # Display the frame with bounding boxes
    processed_frame = results.render()[0]
    # cv2.imshow('YOLOv7 Detection', processed_frame)

    # Print the list of objects and their bounding boxes
    print(f"\n* * * * * * * * * * * * * * * * * * *\n{img} Detected Objects:")
    results.print() 


    for obj, bbox in zip(objects, bounding_boxes):
        print(f"Object: {obj}, Bounding Box: {bbox}")

    # Results
    # results.print()  # or .show(), .save(), .crop(), .pandas(), etc.
    results.show()
    # pan = results.pred
    # print(pan)
    # print()