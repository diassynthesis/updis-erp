__author__ = 'cysnake4713'
from osv import osv, fields


class VoteCategory(osv.osv):
    _name = "updis.vote"
    _description = 'UPDIS Vote Category'
    _order = "name"
    _log_access = True
    _columns = {
        'name': fields.char(size=100, required=True, string="Vote Name"),
        'description': fields.char(size=256, string='Vote Description'),
        'start_time': fields.date(string="Vote Start Time"),
        'end_time': fields.date(string='Vote End Time'),
        'allow_vote_time': fields.integer(string="Each one allowed vote times"),
    }
    _defaults = {
        'allow_vote_time': 1,
    }


    class VoteRecord(osv.osv):
        _name = "updis.vote.record"
        _description = 'UPDIS Vote Record'

        _columns = {
            'vote_category': fields.many2one('updis.vote', string='Vote Category'),
            'author': fields.many2one('hr.employee', string='Author'),
            'content': fields.text("Content"),

        }


    class VoteLog(osv.osv):
        _name = "updis.vote.log"
        _description = 'UPDIS Vote Log'
        _columns = {
            'voter': fields.many2one('res.users', string='Voter'),
            'vote_record': fields.many2one('updis.vote.record', string='Vote record'),
            'vote_time': fields.datetime('Vote Time'),
        }

