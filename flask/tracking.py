import logging
import os

import cv2
import numpy as np
import pandas as pd

logging.basicConfig(filename='tracking.log',
                    format='[%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)
logging.warning("New Run Starts Here")

# This just formats the boxes toi be readable by opencv trackers


def format_points(old_points):
    result = []
    for i in range(0, len(old_points), 2):
        x = old_points[i][0] * 2
        y = old_points[i][1] * 2
        width = old_points[i + 1][0] * 2 - x
        height = old_points[i + 1][1] * 2 - y
        result.append((x, y, width, height))
    return result


def start_trackig(unformated_points, video_id_passed):
    logging.info('start_trackig')
    logging.info(unformated_points)
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

    # Capture the first image
    # TODO: Fail gracefully
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

    count = 0
    # Initiate what will be a list of dataframes.
    # Each dataframe will contain the diaplacements for 1 tissue
    displacement = []

    while True:
        #    logging.info(count)

        """
        if count >= 100:
            break

        """
        # read in the next frame
        successful, image = videostream.read()
        '''
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        cv2.waitKey(20)
        '''
        '''
        if count >= 100:
            break
        '''
        if successful is False:
            break

        # TODO: Add fail
        posts = trackers.update(image)[1]
        postio = {}
        # Get the positions of each post
        for i, post in enumerate(posts):
            # Used float for more acuracy but rectangle needs int
            (x, y, w, h) = [float(i) for i in post]
            # (rx, ry, rw, rh) = [int(i) for i in (x, y, w, h)]
            # cv2.rectangle(image, (rx, ry),
            #              (rx + rw, ry + rh), (0, 255, 0), 2)
            # Populate list for centroid tracking
            centroidX = int((x + x + w) / 2.0)
            centroidY = int((y + y + h) / 2.0)
            postio[i] = (centroidX, centroidY)

        for (objectID, centroid) in postio.items():
            """
            only for debugging showes image and draws boxes on image
            text = "{}".format(objectID)time = self.vs.get(cv2.CAP_PROP_POS_MSEC)/1000
            cv2.putText(image, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(image, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
            logging.info((centroid[0], centroid[1]))

            cv2.imshow("test", image)
            """
            if (objectID % 2) == 0:
                # Save the x position of the even post
                evenX = centroid[0]
                # Save the y position of the even post
                evenY = centroid[1]
                evenID = objectID
                # If objectID is odd it has a pair so do stuff
            elif (objectID - 1) == evenID:
                # Calculate tissue number based on object ID
                reltissueID = int((objectID - 1) / 2)
                if (len(displacement) < reltissueID + 1):
                    displacement.append([])
                # Save the x position of the odd post
                oddX = centroid[0]
                # Save the y position of the odd post
                oddY = centroid[1]

                time = videostream.get(cv2.CAP_PROP_POS_MSEC) / 1000
                disp = np.sqrt(((oddX - evenX)**2) + ((oddY - evenY)**2))
                count = count + 1
                logging.info(count)
                displacement[reltissueID].append(
                    (time, disp, oddX, oddY, evenX, evenY))

    '''
    videostream.release()
    # Closes all the frames
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    '''
    # gets other needed info from tissue object
    date_recorded = video_object.date_recorded
    frequency = video_object.frequency
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
# REVIEW: vid save loaction to full path csv save loaction is from static
    for i, an in enumerate(displacement):
        df = pd.DataFrame(
            an, columns=["time", "disp", "oddX", "oddY", "evenX", "evenY"])
        path_to_csv = directory_to_save_path + '{0}_T{1}_F{2}.csv'.format(
            date_as_string, li_tissue_numbers[i],  frequency)
        df.to_csv(path_to_csv, index=False)
        models.add_tissue_csv(li_tissue_ids[i], path_to_csv)
    logging.info("check csv")

    # deltes files in img folder
    # REVIEW: this can probally be done better
    for file in os.listdir(os.getcwd() + '/static/img'):
        os.remove(os.getcwd() + '/static/img/' + file)

    return boxes
