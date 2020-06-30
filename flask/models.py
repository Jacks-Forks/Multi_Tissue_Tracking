from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# TODO: need to do more robust test to esure realtionships are working but appears to be
# TODO: ensure adding process works
# TODO: what hnappens when get fails check that work flow


class Experiment(db.Model):
    # TODO: can i get ride of number just use id?
    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Integer, nullable=False)
    tissues = db.relationship('Tissue', back_populates='experiment')
    vids = db.relationship('Video', back_populates='experiment')


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: change to eastern time????
    # TODO: datetime vs date proablly only need date
    date_uploaded = db.Column(db.Date, nullable=False,
                              default=datetime.now())
    date_recorded = db.Column(db.Date, nullable=False)

    experiment_num = db.Column(db.Integer, db.ForeignKey(
        'experiment.num'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='vids')

    tissues = db.relationship('Tissue', back_populates='video')


class Tissue(db.Model):
    # TODO: pk maybe should be combo between tissue number and expirment number
    id = db.Column(db.Integer, primary_key=True)
    tissue_number = db.Column(db.Integer, nullable=False)
    tissue_type = db.Column(db.String(120), nullable=False)
    post = db.Column(db.Integer, nullable=False)

    experiment_num = db.Column(db.Integer, db.ForeignKey(
        'experiment.num'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='tissues')

    bio_reactor_id = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.id'), nullable=False)
    bio_reactor = db.relationship('Bio_reactor', back_populates='tissues')

    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video = db.relationship('Video', back_populates='tissues')

    def __repr__(self):
        return '<UTissue %r>' % self.tissue_number

# TODO: video and csv separe or not


class Bio_reactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tissues = db.relationship('Tissue', back_populates='bio_reactor')
    # TODO:put actual stuff here


def insert_experiment(num_passed):
    new_expirment = Experiment(num=num_passed)
    db.session.add(new_expirment)
    db.session.commit()


def get_experiment(experiment_num_passed):
    # TODO: get expirenmeint if one does not exist call create expirment
    # TODO: adderror handling
    expirment = Experiment.query.filter_by(num=experiment_num_passed).first()
    if expirment is None:
        insert_experiment(experiment_num_passed)
    return expirment


def insert_video(date_recorded_passed, experiment_num_passed):
    # TODO: add bio reactior
    new_video = Video(date_recorded=date_recorded_passed,
                      experiment_num=experiment_num_passed)
    new_video.expirment = get_experiment(experiment_num_passed)
    db.session.add(new_video)
    db.session.commit()
    return new_video


def get_bio_reactor(bio_reactor_id_passed):
    bio_reactor = Bio_reactor.query.filter_by(id=bio_reactor_id_passed).first()
    return bio_reactor


def insert_tissue_sample(tissue_number_passed, tissue_type_passed, experiment_num_passed, bio_reactor_id_passed, post_passed, video_id_passed):
    new_tissue = Tissue(
        tissue_number=tissue_number_passed, tissue_type=tissue_type_passed, post=post_passed, experiment_num=experiment_num_passed, video_id=video_id_passed, bio_reactor_id=bio_reactor_id_passed)
    new_tissue.experiment = get_experiment(experiment_num_passed)
    new_tissue.bio_reactor = get_bio_reactor(bio_reactor_id_passed)
    new_tissue.video = get_video(video_id_passed)
    db.session.add(new_tissue)
    db.session.commit()


def insert_bio_reactor():
    new_bio_reactor = Bio_reactor()
    db.session.add(new_bio_reactor)
    db.session.commit()
    return new_bio_reactor


def get_tissue(tissue_id_passed):
    tissue = Tissue.query.filter_by(id=tissue_id_passed).first()
    return tissue


def get_video(video_id_passed):
    video = Video.query.filter_by(id=video_id_passed).first()
    if video is None:
        video = insert_video(video_id_passed)
    return video
