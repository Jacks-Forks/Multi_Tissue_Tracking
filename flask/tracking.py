import logging
import os

import cv2
import dashSelect as path
import models
import numpy as np
import pandas as pd

logging.basicConfig(filename='tracking.log', level=logging.DEBUG)
logging.warning("New Run Starts Here")


def format_points(old_points):
    result = []
    for i in range(0, len(old_points), 2):
        x = old_points[i][0] * 2
        y = old_points[i][1] * 2
        width = old_points[i + 1][0] * 2 - x
        height = old_points[i + 1][1] * 2 - y
        result.append((x, y, width, height))
    return result


def start_trackig(unformated_points, file_path, experiment_num_passed, date_recorded_passed, frequency_passed, li_tissue_nums_passed):
    # logging.info(path.filer)
    logging.info('start_trackig')
    logging.info(unformated_points)
    logging.info(file_path)

    videostream = cv2.VideoCapture(file_path)
    splits = file_path.split('/')
    images = videostream.read()[1]

    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }

    trackers = cv2.MultiTracker_create()

    boxes = format_points(unformated_points)

    for box in boxes:
        tracker = OPENCV_OBJECT_TRACKERS['csrt']()
        trackers.add(tracker, images, box)

    count = 0
    displacement = []

    # fig = go.Figure()
    # trace = fig.add_trace(go.Scatter(x=xox, y=lists))
    while True:
        #    logging.info(count)

        """
        if count >= 100:
            break

        """
        # TODO: need should this have ret and [1] seems to stop evntually
        # does 1489 in csv
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
        posts = trackers.update(image)[1]
        postcords = []

        for post in posts:
            # Used float for more acuracy but rectangle needs int
            (x, y, w, h) = [float(i) for i in post]
            # (rx, ry, rw, rh) = [int(i) for i in (x, y, w, h)]
            # cv2.rectangle(image, (rx, ry),
            #              (rx + rw, ry + rh), (0, 255, 0), 2)
            # Populate list for centroid tracking
            postcords.append((x, y, x + w, y + h))

        postio = {}

        for (i, (x, y, x2, y2)) in enumerate(postcords):
            centroidX = int((x + x2) / 2.0)
            centroidY = int((y + y2) / 2.0)
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

    date_as_string = date_recorded_passed.strftime('%m_%d_%Y')
    directory_to_save_path = 'static/uploads/' + \
        str(experiment_num_passed) + '/csvfiles/' + date_as_string + "/"
    if not os.path.exists(directory_to_save_path):
        os.makedirs(directory_to_save_path)

    for i, an in enumerate(displacement):
        df = pd.DataFrame(
            an, columns=["time", "disp", "oddX", "oddY", "evenX", "evenY"])
        df.to_csv(directory_to_save_path + '{0}_T{1}_{2}_.csv'.format(
            date_recorded_passed, li_tissue_nums_passed[i],  frequency_passed), index=False)
    print("check CSV")
    return boxes
