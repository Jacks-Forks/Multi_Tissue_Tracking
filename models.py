from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

'''
class Bio_reactor_A_sample(db.Model):
    # TODO: this need to be reforated to actally match reactor
    id = db.Column(db.Integer, primary_key=True)
    date_recorded = db.Column(db.Date, nullable=False)
    date_uploaded = db.Column(db.Date, nullable=False)
    num_tissues = db.Column(db.Integer)
    file_location = db.Column(db.String(120))

    def __repr__(self):
        return '<Uploaded_file %r>' % self.id


class Bio_reactor_B_sample(db.Model):
    # for each post it it either string empty of a string with the format tissume_number , type_of_tissue
    id = db.Column(db.Integer, primary_key=True)
    date_recorded = db.Column(db.Date, nullable=False)
    date_uploaded = db.Column(db.Date, nullable=False)
    num_tissues = db.Column(db.Integer)
    post_zero = db.Column(db.String(120))
    post_one = db.Column(db.String(120))
    post_two = db.Column(db.String(120))
    post_three = db.Column(db.String(120))
    post_four = db.Column(db.String(120))
    post_five = db.Column(db.String(120))
    #  TODO: does this need to be saved and is it a good formant
    file_location = db.Column(db.String(120))

    def __repr__(self):
        return '<Uploaded_file %r>' % self.id + str(self.date_recorded) + str(self.date_uploaded) + str(self.num_tissues) + self.post_zero + self.post_one + self.post_two + self.post_three + self.post_four + self.post_five + self.file_location
'''


def insert_bio_sample(bio_sample):
    db.session.add(bio_sample)
    db.session.commit()


def insert_tissue_sample(tissue_sample):
    #    experimentTest = Experiment()
    #    tissue_sample.experiment.append(experimentTest)
    db.session.add(tissue_sample)
    db.session.commit()
    print('added')


class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tissues = db.relationship('Tissue', back_populates='experiment')
    vids = db.relationship('Video', back_populates='experiment')


class Tissue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tissue_number = db.Column(db.Integer, nullable=False)
    tissue_type = db.Column(db.String(120), nullable=False)
    experiment_id = db.Column(db.Integer, db.ForeignKey(
        'experiment.id'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='tissues')

    bio_reactor_id = db.Column(db.Integer, db.ForeignKey(
        'bio_reactor.id'), nullable=False)
    bio_reactor = db.relationship('Bio_reactor', back_populates='tissues')
    post = db.Column(db.Integer, nullable=False)

    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    video = db.relationship('Video', back_populates='tissues')

# TODO: video and csv separe or not


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # TODO: change to eastern time????
    # TODO: datetime vs date proablly only need date
    date_uploaded = db.Column(db.Date, nullable=False,
                              default=datetime.now())
    date_recorded = db.Column(db.Date, nullable=False)

    experiment_id = db.Column(db.Integer, db.ForeignKey(
        'experiment.id'), nullable=False)
    experiment = db.relationship('Experiment', back_populates='vids')

    tissues = db.relationship('Tissue', back_populates='video')


class Bio_reactor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tissues = db.relationship('Tissue', back_populates='bio_reactor')
    # TODO:put actual stuff here
