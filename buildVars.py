# -*- coding: UTF-8 -*-

# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

# Full getext (please don't change)
_ = lambda x : x

# Add-on information variables

addon_info = {
	# for previously unpublished addons, please follow the community guidelines at:
	# https://bitbucket.org/nvdaaddonteam/todo/raw/master/guideLines.txt
	# add-on Name, internal for nvda
	"addon_name" : "audacity",
	# Add-on summary, usually the user visible name of the addon.
	# Translators: Summary for this add-on to be shown on installation and add-on information.
	"addon_summary" : _("Audacity"),
	# Add-on description
	# Translators: Long description to be shown for this add-on on add-on information from add-ons manager
	"addon_description" : _("""This add-on adds extra functionality when working with Audacity

* a script to report audio position,
* a script to report start and end of selection,
* automatic audio position changes report ,
* automatic selection changes report (can be disabled),
* timer control editting support,
* use of spacebar to press a button,
* script to report playback/recording peak level,
* script to report playback/record slider level,
* script to report playback speed,
* script to display add-on user manual,
* script to display audacity guide written by David Bailes.


This addon's version has been tested with NVDA 2017.4, NVDA 2017.3 and audacity v2.2.1 and v2.2.0.  Previous versions of Audacity are not  supported.
"""),
	# version
	"addon_version" : "3.1",
	# Author(s)
	"addon_author" : u"paulber007",
	# URL for the add-on documentation support
	"addon_url" : "paulber007@wanadoo.fr",
	# Documentation file name
	"addon_docFileName" : "addonUserManual.html",
	#for readme.md file, link to download last stable version
	"stableVersionLink" : "https://rawgit.com/paulber007/AllMyNVDAAddons/master/audacity/audacity-3.1.nvda-addon",
	# for readme.md file, link to download current development version
	"devVersionLink": "https://rawgit.com/paulber007/AllMyNVDAAddons/master/audacity/audacity-3.1.nvda-addon",
	}


import os.path

# Define the python files that are the sources of your add-on.
# You can use glob expressions here, they will be expanded.
pythonSources = [os.path.join("addon", "*.py"), os.path.join("addon", "appModules", "*.py"), os.path.join("addon", "appModules", "audacityPackage", "*.py")
]

# Files that contain strings for translation. Usually your python sources
i18nSources = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
# Paths are relative to the addon directory, not to the root directory of your addon sources.
excludedFiles = []

# Translators:  strings used to generate  readme.md file
readmeStrings = {"stableVersionDownload": _("Download [stable version]"),"devVersionDownload":  _("Download [development version]"), "author": _("Author"), "url": _("URL")}

