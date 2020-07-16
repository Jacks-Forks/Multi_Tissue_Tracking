import logging
from datetime import datetime

from pytz import timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

tz = timezone('EST')
# TODO: need to do more robust test to esure realtionships are working but appears to be
# TODO: ensure adding process works
# TODO: what hnappens when get fails check that work flow


class Experiment(db.Model):
    experiment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_num = db.Column(
        db.Integer, nullable=False, unique=True)
    tissues = db.relationship(
        'Tissue', back_populates='experiment', passive_deletes=True)
    vids = db.relationship(
        'Video', back_populates='experiment', passive_deletes=True)


class Video(db.Model):
    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # TODO: add call factor float
    date_uploaded = db.Column(db.Date, nullable=False,
                              default=datetime.now(tz))
    date_recorded = db.Column(db.Date, nullable=False)

    frequency = db.Column(db.Float, nullable=False)

    save_location = db.Column(db.String(120), nullable=False)

    experiment_num = db.Column(db.Integer, db.ForeignKey(
        'experiment.experiment_num'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='vids')

    bio_reactor_num = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.bio_reactor_num', ondelete='CASCADE'), nullable=False)
    bio_reactor = db.relationship(
        'Bio_reactor', back_populates='vids')

    tissues = db.relationship(
        'Tissue', back_populates='video', passive_deletes=True)


class Tissue(db.Model):
    # REVIEW: pk maybe should be combo between tissue number and expirment number
    tissue_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tissue_number = db.Column(db.Integer, nullable=False)
    tissue_type = db.Column(db.String(120), nullable=False)
    post = db.Column(db.Integer, nullable=False)
    csv_path = db.Column(db.String(120), nullable=True)

    experiment_num = db.Column(db.Integer, db.ForeignKey(
        'experiment.experiment_num'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='tissues')

    bio_reactor_num = db.Column(db.Integer,  db.ForeignKey(
        'bio_reactor.bio_reactor_num', ondelete='CASCADE'), nullable=False)
    bio_reactor = db.relationship(
        'Bio_reactor', back_populates='tissues')

    video_id = db.Column(
        db.Integer,  db.ForeignKey('video.video_id', ondelete='CASCADE'), nullable=False)
    video = db.relationship(
        'Video', back_populates='tissues')

    def __repr__(self):
        return '<Tissue %r>' % self.id

# TODO: video and csv separe or not


class Bio_reactor(db.Model):
    bio_reactor_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    bio_reactor_num = db.Column(db.Integer, unique=True, nullable=False)
    tissues = db.relationship('Tissue', back_populates='bio_reactor')
    vids = db.relationship('Video', back_populates='bio_reactor')
    # TODO:put actual stuff here

# TODO: what happens if already exsits?


def insert_experiment(num_passed):
    new_expirment = Experiment(experiment_num=num_passed)
    db.session.add(new_expirment)
    db.session.commit()


def insert_video(date_recorded_passed, experiment_num_passed, bio_reactor_num_passed, frequency_passed, save_path_passed):

    new_video = Video(date_recorded=date_recorded_passed,
                      experiment_num=experiment_num_passed, bio_reactor_num=bio_reactor_num_passed, frequency=frequency_passed, save_location=save_path_passed)
    new_video.expirment = get_experiment(experiment_num_passed)
    new_video.bio_reactor = get_bio_reactor(bio_reactor_num_passed)

    db.session.add(new_video)
    db.session.commit()
    return new_video.video_id


def insert_tissue_sample(tissue_number_passed, tissue_type_passed, experiment_num_passed, bio_reactor_num_passed, post_passed, video_id_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, experiment_num=experiment_num_passed, video_id=video_id_passed, bio_reactor_num=bio_reactor_num_passed)
    new_tissue.experiment = get_experiment(experiment_num_passed)
    new_tissue.bio_reactor = get_bio_reactor(bio_reactor_num_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_tissue_sample_csv(tissue_number_passed, tissue_type_passed, experiment_num_passed, bio_reactor_num_passed, post_passed, video_id_passed, csv_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, experiment_num=experiment_num_passed, video_id=video_id_passed, bio_reactor_num=bio_reactor_num_passed, csv_path=csv_passed)
    new_tissue.experiment = get_experiment(experiment_num_passed)
    new_tissue.bio_reactor = get_bio_reactor(bio_reactor_num_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_bio_reactor(num_passed):
    new_bio_reactor = Bio_reactor(bio_reactor_num=num_passed)
    db.session.add(new_bio_reactor)
    db.session.commit()

# TODO: add error handling for all get functions


def get_experiment(experiment_num_passed):
    expirment = Experiment.query.filter_by(
        experiment_num=experiment_num_passed).first()
    return expirment


def get_bio_reactor(bio_reactor_num_passed):
    bio_reactor = Bio_reactor.query.filter_by(
        bio_reactor_num=bio_reactor_num_passed).first()
    return bio_reactor


def get_tissue(tissue_id_passed):
    # gets tissue by the tissue id
    tissue = Tissue.query.filter_by(tissue_id=tissue_id_passed).first()
    return tissue


def get_dates_list(experiment_num_passed):
    experiment = get_experiment(experiment_num_passed)
    videos_list = experiment.vids
    dates = []
    for video in videos_list:
        if video.date_recorded not in dates:
            dates.append(video.date_recorded)
    return dates


def get_tissue_by_csv(csv_filepath):
    # gets tissue by the tissue id
    logging.info('csvpath')
    logging.info(csv_filepath)
    tissue = db.session.query(Tissue).filter_by(csv_path=csv_filepath).first()
    logging.info(tissue)
    return tissue


def get_video(video_id_passed):
    video = Video.query.filter_by(video_id=video_id_passed).first()
    return video


def add_tissue_csv(id_passed, path_passed):
    tissue = get_tissue(id_passed)
    tissue.csv_path = path_passed
    db.session.commit()


def get_all_experiments():
    experment_list = []
    experiments = Experiment.query.all()
    for exp in experiments:
        dic = {'experment_id': exp.experiment_id,
               'experment_num': exp.experiment_num}
        experment_list.append(dic)
    return experment_list


def get_all_videos():
    vid_list = []
    vids = Video.query.all()
    for video in vids:
        dic = {'id': video.video_id, 'date_uploaded': video.date_uploaded, 'date_recorded': video.date_recorded, 'frequency': video.frequency,
               'save_location': video.save_location, 'bio_reactor_num': video.bio_reactor_num, 'experiment_num': video.experiment_num}
        vid_list.append(dic)
    return vid_list


def get_all_tissues():
    tissue_list = []
    tissues = Tissue.query.all()
    for tissue in tissues:
        dic = {'tissue_id': tissue.tissue_id, 'tissue_number': tissue.tissue_number,
               'tissue_type': tissue.tissue_type, 'post': tissue.post, 'csv_path': tissue.csv_path, 'experiment_num': tissue.experiment_num, 'bio_reactor_num': tissue.bio_reactor_num, 'video_id': tissue.video_id}
        tissue_list.append(dic)
    return tissue_list


def get_all_bio_reactors():
    bio_list = []
    bio_reactors = Bio_reactor.query.all()
    for bio in bio_reactors:
        dic = {'bio_id': bio.bio_reactor_id, 'bio_num': bio.bio_reactor_num}
    bio_list.append(dic)
    return bio_list


def delete_tissue(tissue_id):
    tissue = get_tissue(tissue_id)
    db.session.delete(tissue)
    db.session.commit()


def delete_video(vid_id):
    vid = get_video(vid_id)
    db.session.delete(vid)
    db.session.commit()


def delete_expirement(exp_id):
    exp = get_experiment(exp_id)
    db.session.delete(exp)
    db.session.commit()


def delete_bio_reactor(bio_id):
    bio = get_bio_reactor(bio_id)
    db.session.delete(bio)
    db.session.commit()
