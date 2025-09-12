# --------------------------------------
#       Shortcut for apmodel
# --------------------------------------

# ActivityStreams Core
from apmodel.core import (
    Activity,  # noqa: F401
    Collection,  # noqa: F401
    CollectionPage,  # noqa: F401
    Object,  # noqa: F401
    OrderedCollection,  # noqa: F401
    OrderedCollectionPage,  # noqa: F401
)

# ActivityStreams Vocab
from apmodel.vocab.actor import Actor, Person, Application, Group, Organization, Service  # noqa: F401
from apmodel.vocab.article import Article  # noqa: F401
from apmodel.vocab.document import Document, Audio, Image, Video, Page  # noqa: F401
from apmodel.vocab.event import Event, Place  # noqa: F401
from apmodel.vocab.mention import Mention  # noqa: F401
from apmodel.vocab.note import Note  # noqa: F401
from apmodel.vocab.profile import Profile  # noqa: F401
from apmodel.vocab.tombstone import Tombstone  # noqa: F401

from apmodel.vocab.activity.accept import Accept, TentativeAccept  # noqa: F401
from apmodel.vocab.activity.add import Add  # noqa: F401
from apmodel.vocab.activity.announce import Announce  # noqa: F401
from apmodel.vocab.activity.arrive import Arrive  # noqa: F401
from apmodel.vocab.activity.block import Block  # noqa: F401
from apmodel.vocab.activity.create import Create  # noqa: F401
from apmodel.vocab.activity.delete import Delete  # noqa: F401
from apmodel.vocab.activity.dislike import Dislike  # noqa: F401
from apmodel.vocab.activity.flag import Flag  # noqa: F401
from apmodel.vocab.activity.follow import Follow  # noqa: F401
from apmodel.vocab.activity.ignore import Ignore  # noqa: F401
from apmodel.vocab.activity.invite import Invite  # noqa: F401
from apmodel.vocab.activity.join import Join  # noqa: F401
from apmodel.vocab.activity.leave import Leave  # noqa: F401
from apmodel.vocab.activity.like import Like  # noqa: F401
from apmodel.vocab.activity.listen import Listen  # noqa: F401
from apmodel.vocab.activity.move import Move  # noqa: F401
from apmodel.vocab.activity.offer import Offer  # noqa: F401
from apmodel.vocab.activity.question import Question  # noqa: F401
from apmodel.vocab.activity.read import Read  # noqa: F401
from apmodel.vocab.activity.reject import Reject, TentativeReject  # noqa: F401
from apmodel.vocab.activity.remove import Remove  # noqa: F401
from apmodel.vocab.activity.travel import Travel  # noqa: F401
from apmodel.vocab.activity.undo import Undo  # noqa: F401
from apmodel.vocab.activity.update import Update  # noqa: F401
from apmodel.vocab.activity.view import View  # noqa: F401

# Extra models
from apmodel.extra import Emoji, Hashtag  # noqa: F401
from apmodel.extra.cid import Multikey, DataIntegrityProof  # noqa: F401
from apmodel.extra.schema import PropertyValue  # noqa: F401
from apmodel.extra.security import CryptographicKey  # noqa: F401

# Nodeinfo
from apmodel.nodeinfo.nodeinfo import (
    Nodeinfo,  # noqa: F401
    NodeinfoInbound,  # noqa: F401
    NodeinfoOutbound,  # noqa: F401
    NodeinfoProtocol,  # noqa: F401
    NodeinfoServices,  # noqa: F401
    NodeinfoSoftware,  # noqa: F401
    NodeinfoUsage,  # noqa: F401
    NodeinfoUsageUsers,  # noqa: F401
)

# Base Types
from apmodel.types import (
    ActivityPubModel,  # noqa: F401
    Undefined  # noqa: F401
)