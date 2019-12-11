from peewee import fn, SQL
from app.models import Comment, RejectedComment


def total_comments():
    approved = Comment.select(Comment.id).count()
    rejected = RejectedComment.select(RejectedComment.id).count()
    return {'approved': approved,
            'rejected': rejected,
            'total': approved + rejected}


def weekly_comments():
    approved = Comment.select \
        (fn.date_trunc('week', Comment.created), fn.COUNT(Comment.id)) \
        .group_by(fn.date_trunc('week', Comment.created)) \
        .order_by(SQL('date_trunc').asc())

    rejected = RejectedComment.select \
        (fn.date_trunc('week', RejectedComment.created), fn.COUNT(RejectedComment.id)) \
        .group_by(fn.date_trunc('week', RejectedComment.created)) \
        .order_by(SQL('date_trunc').asc())

    data = zip(approved.tuples(), rejected.tuples())
    return [(w1.date, c, (c + rc), round(c*100/(c+rc))) for (w1, c), (w2, rc) in data]


def hourly_comments():
    q = Comment.select \
        (fn.date_part('hour', Comment.created), fn.COUNT(Comment.id)) \
        .group_by(fn.date_part('hour', Comment.created)) \
        .order_by(SQL('date_part').asc()).tuples()
    return tuple((h, c) for (h, c) in q)
