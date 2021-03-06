"""Components that validate against types and interfaces."""

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *

from Products.Relations import brain, exception, ruleset, interfaces, utils
from Products.Relations.config import *
from Products.Relations.schema import BaseSchemaWithInvisibleId

# Maybe some day we will get consistency on how implements works
# so that we don't have to do this - cwarner
from zope.interface import implements
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.interfaces import IExtensibleMetadata


class PortalTypeConstraint(BaseContent, ruleset.RuleBase):
    """A validator and vocabulary provider, restricting sources and targets
    by portal type."""
    implements(interfaces.IVocabularyProvider, interfaces.IValidator,
            IBaseContent, IReferenceable, IExtensibleMetadata)

    content_icon = 'portaltypeconstraint_icon.gif'

    # IVocabularyProvider
    def makeVocabulary(self, source, targets=None):
        # source type not valid
        ast = self.getAllowedSourceTypes()
        att = self.getAllowedTargetTypes()
        if ast and source.portal_type not in ast:
            return []
        
        if targets is not None: # filter
            return [t for t in targets if not att or t.portal_type in att]

        else: # create list
            uc = getToolByName(self, UID_CATALOG)
            objs = uc(**self.getSearchTerms())
            return [brain.makeBrainAggregate(self, o) for o in objs]

    def getSearchTerms(self):
        d = {}
        att = self.getAllowedTargetTypes()
        if att:
            d['portal_type'] = att
        return d

    # IValidator
    def validateConnected(self, reference, chain):
        ast = self.getAllowedSourceTypes()
        att = self.getAllowedTargetTypes()
        st = reference.getSourceBrain().portal_type
        tt = reference.getTargetBrain().portal_type

        # XXX: i18n
        if ast:
            if st not in ast:
                raise exception.ValidationException(
                    "Source type %s not allowed for '%s'." %
                    (st, self.getRuleset().Title()), reference, chain)
        if att:
            if tt not in att:
                raise exception.ValidationException(
                    "Target type %s not allowed for '%s'." %
                    (tt, self.getRuleset().Title()), reference, chain)

    def validateDisconnected(self, reference, chain):
        "Don't care."

    # Archetypes implementation
    schema = BaseSchemaWithInvisibleId + Schema((
        LinesField('allowedSourceTypes',
                   vocabulary='_allowedTypesVocabulary',
                   enforceVocabulary=True,
                   widget=MultiSelectionWidget(label='Allowed Source Types',
                                       label_msgid='label_relation_allowsrctypes',
                                       #description="A description...",
                                       #description_msgid='help_relation_primary',
                                       i18n_domain='Relations',),),

        LinesField('allowedTargetTypes',
                   vocabulary='_allowedTypesVocabulary',
                   enforceVocabulary=True,
                   widget=MultiSelectionWidget(label='Allowed Target Types',
                                       label_msgid='label_relation_allowtargtypes',
                                       #description="A description...",
                                       #description_msgid='help_relation_primary',
                                       i18n_domain='Relations',),),
        ))
    portal_type = 'Type Constraint'

    def _allowedTypesVocabulary(self):
        return DisplayList(
            [(pt, pt) for pt in utils.getReferenceableTypes(self)])

registerType(PortalTypeConstraint, PROJECTNAME)

class InterfaceConstraint(PortalTypeConstraint):
    """A validator and vocabulary provider, restricting sources and targets
    by interfaces they implement."""

    def getAllowedSourceTypes(self):
        asi = self.getAllowedSourceInterfaces()
        if asi:
            return self._getPortalTypesByInterfaces(asi)
        else:
            return []

    def getAllowedTargetTypes(self):
        ati = self.getAllowedTargetInterfaces()
        if ati:
            return self._getPortalTypesByInterfaces(ati)
        else:
            return []

    def _getPortalTypesByInterfaces(self, allowed):
        portal_types = utils.getPortalTypesByInterfaces(self, allowed)
        # This is needed so PortalTypeConstraint doesn't believe we have
        # nothing selected, i.e. all allowed:
        portal_types.append('spam')
        return portal_types

    schema = BaseSchemaWithInvisibleId + Schema((
        LinesField('allowedSourceInterfaces',
                    widget=LinesWidget(label='Allowed Source Interfaces',
                                       label_msgid='label_relation_allowsrcinterface',
                                       #description="A description...",
                                       #description_msgid='help_relation_primary',
                                       i18n_domain='Relations',),),
        LinesField('allowedTargetInterfaces',
                    widget=LinesWidget(label='Allowed Target Interfaces',
                                       label_msgid='label_relation_allowtarginterface',
                                       #description="A description...",
                                       #description_msgid='help_relation_primary',
                                       i18n_domain='Relations',),),
        ))
    archetype_name = portal_type = 'Interface Constraint'

registerType(InterfaceConstraint, PROJECTNAME)
    
