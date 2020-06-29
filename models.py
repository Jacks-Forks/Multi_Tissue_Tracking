from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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


def insert_bio_sample(bio_sample):
    db.session.add(bio_sample)
    db.session.commit()
