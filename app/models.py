from app import db


class Classifier(db.Model):
    name = db.Column(db.String(128), primary_key=True)
    conversations = db.relationship("Conversation")

    def __repr__(self):
        return '<Classifier {}>'.format(self.name)


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(128), unique=False)
    types = db.Column(db.Boolean, nullable=True, default=None)
    data = db.Column(db.JSON)
    model = db.Column(db.String(128), db.ForeignKey('classifier.name'))

    def __repr__(self):
        return '<Conversation {}>'.format(self.data)