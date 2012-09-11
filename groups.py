#!/usr/bin/python

'''
 627 def _getLatestGroupAppliance(self, auth, project, stage):
 628 logutil.info("_getLatestGroupAppliance")
 629 repository_search = restutil.get(stage.project_branch_stage.groups.href, auth=auth)
 630 matches = helpers.getXpathMatchList(repository_search,
 631 "/troves/trove[name='group-%s-appliance']" % project.project.short_name)
 632 asserts.fail_unless(len(matches) > 0, "Could not find any built group for this product.")
 633 group_versions = [x.trove.trailingVersion for x in matches]
 634 group_versions.sort()
 635 trailing_version = group_versions[-1]
 636 matches = [match for match in matches if match.trove.trailingVersion == trailing_version]
 637 return matches 
 '''
