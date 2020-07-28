import logging
import os

import cv2
import pandas as pd
from scipy.spatial import distance

logging.basicConfig(filename='tracking.log',
                    format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.warning("New Run Starts Here")


# This just formats the boxes toi be readable by opencv trackers


def format_points(old_points):
    result = []
    for i in range(0, len(old_points), 2):
        # Multiply by 2 because of scale factopr
        x = old_points[i][0] * 2
        y = old_points[i][1] * 2
        width = old_points[i + 1][0] * 2 - x
        height = old_points[i + 1][1] * 2 - y
        result.append((x, y, width, height))
    return result


def start_trackig(unformated_points, video_id_passed, calib_factor):
    logging.info('start_trackig')
    # allows acess to the databse avoding circular imports
    # REVIEW: there might be a better way to do this
    from app import app
    app.app_context().push()
    import models

    # gets the videio object from the db using the id from the ajax request
    video_object = models.get_video(video_id_passed)

    # getsvidio file path from vid object
    video_file_path = video_object.save_location

    # Start a opencv videostream
    videostream = cv2.VideoCapture(video_file_path)
    total_frames = int(videostream.get(cv2.CAP_PROP_FRAME_COUNT))

    # Capture the first image
    # TODO: Faddil gracefully
    images = videostream.read()[1]

    # Iniate all the available opencv trackers
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }

    # Create a multitracker object
    trackers = cv2.MultiTracker_create()

    # Format the points for opencv
    boxes = format_points(unformated_points)

    for box in boxes:
        # Create and add a tracker to the multitracker object for each box drawn
        tracker = OPENCV_OBJECT_TRACKERS['csrt']()
        trackers.add(tracker, images, box)

    frame = 1
    old_percentage = 0
    # Initiate what will be a list of dataframes.
    # Each dataframe will contain the diaplacements for 1 tissue
    displacement = []

    while True:
        if (percentage := int(100 * frame / total_frames)) is not old_percentage:
            print(percentage)
        old_percentage = percentage

        # read in the next frame
        successful, image = videostream.read()
        if not successful:
            logging.info("tracker failed to follow object")
            break
        frame += 1

        successful, posts = trackers.update(image)
        if not successful:
            break

        # Get the positions of each post
        for objectID, post in enumerate(posts):
            (x, y, w, h) = [float(i) for i in post]
            centroid = (float(x + w / 2), float(y + h / 2))

            # Divide by two because of the scale factor of the video
            def calibrate(centroids): return (
                centroids[0] * calib_factor / 2, centroids[1] * calib_factor / 2)

            if (objectID % 2) == 0:
                # Save the x, y position of the even post
                centroid_even = calibrate(centroid)
                evenID = objectID
            # If objectID is odd it has a pair so do stuff
            elif (objectID - 1) == evenID:
                # Calculate tissue number based on object ID
                reltissueID = int((objectID - 1) / 2)

                if len(displacement) < reltissueID + 1:
                    displacement.append([])

                # Save the x, y position of the odd post
                centroid_odd = calibrate(centroid)
                time = videostream.get(cv2.CAP_PROP_POS_MSEC) / 1000

                disp = distance.euclidean(centroid_even, centroid_odd)
                displacement[reltissueID].append(
                    (time, disp, centroid_odd[0], centroid_odd[1], centroid_even[0], centroid_even[1]))

    # gets other needed info from video object
    date_recorded = video_object.date_recorded
    frequency = video_object.frequency
    frequencyUnder = str(frequency).replace('.', '-')
    experiment_num = video_object.experiment_num

    # list of tissue objects that are childeren of the vid
    tissue_object_list = video_object.tissues
    # gets the id and numbers of the tissues from db
    li_tissue_ids = [tissue.tissue_id for tissue in tissue_object_list]
    li_tissue_numbers = [
        tissue.tissue_number for tissue in tissue_object_list]

    date_as_string = date_recorded.strftime('%m_%d_%Y')

    directory_to_save_path = 'static/uploads/' + \
        str(experiment_num) + "/" + date_as_string + '/csvfiles/'

    if not os.path.exists(directory_to_save_path):
        os.makedirs(directory_to_save_path)
    for i, an in enumerate(displacement):
        df = pd.DataFrame(
            an, columns=["time", "disp", "oddX", "oddY", "evenX", "evenY"])
        path_to_csv = directory_to_save_path + \
            f'{date_as_string}_T{li_tissue_numbers[i]}_F{frequencyUnder}.csv'
        logging.info(path_to_csv)
        df.to_csv(path_to_csv, index=False)
        models.add_tissue_csv(li_tissue_ids[i], path_to_csv)
    logging.info("check csv")

    # deletes files in img folder
    # REVIEW: this can probally be done better
    for file in os.listdir(os.getcwd() + '/static/img'):
        os.remove(os.getcwd() + '/static/img/' + file)

    return boxes
