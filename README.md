EZDM is a free/open-source toolkit for dungeons and dragons dungeon-masters

![EZDM Screenshot](screenshot2.png?raw=true "EZDM2.0")

Version 2.0 is a near-complete rewrite of the original code with massive improvements and much
higher code quality in a truly elegant design.
EZDM encapsulates virtually all of the ADnD2E ruleset in json data files, and could be adapted
for other editions or different gaming systems with relative ease as nearly all the changes
will be in the data files only (you would need to create child-class of Character and override
some methods however as these are based on interpreting the 2E specific data). The system is based
on python combined with json for data and jinja2 as the templating engine for the web-based gui.

Usage: start the ezdm server and point your browser to: http://localhost:8000

The library and data system could, with relative ease be adapted to become the engine for an RPG
game, either using party or single-player mode but some functionality would have to be added.
I would like to do so at some point.

As of version 2.0 the system has two distinct modes of operation, which you can swith between at will.
In Dungeon Master mode, you get the capacity to edit the data files for your personal campaigns by hand.
You would use this to initially create character sheets for players, design maps or 
create spells and items. 
In Campaign mode the tools behave more like a game, displaying the (revealed parts of the) map and activities 
based on that or, when needed, the combat engine.All of this is turn-based in true DND style.
As a dungeon master preparing for a session you will likely switch between these modes frequently as you 
access various tools to prepare (and test) portions of the campaign.
The system ships with some sample data, while any you add are saved in your home directory.
You can also add other directories by editing /etc/ezdm/settings.py.

EZDM is not a complete replacement for your normal DM role nor is it intended to be, it's job is merely
to let you focus on story-telling while doing the hard maths for you. 

Core tools: 
Dungeon Master mode:
	Character Sheet editor (for players and monsters)
	Item Editor
	Map Editor
Campaign Mode:
	Map Viewer/Navigator (hiding unrevealed parts) - behaves much like roguelikes do.
	Combat Engine:
      The combat engine is integrated into the rest of the tools - you attack view the map view and 
      EZDM handles the atack and damage rolls according to the rules for you. Spells casts and item
      views likewise are triggered from the spellbook and inventory
	Character sheet view.
	Inventory management.
    Spellbook.

Magic:
Perhaps the hardest part to implement in EZDM was magic, in all it's sources. EZDM handles this in a
very elegant manner however. All items can, potentially, have magical effects - and spells are just a type
of Item which is kept in a special inventory slot.
The json files holding the data for items have a section called "events".
Within this are subkeys for various supported events. Within these subkeys you implement magic by writing 
short python snippets.
The snippets run in a tightly constrained environment, but depending on the event have access to the objects
they need to manipulate in order to function. The item template automatically inserts a small sample
"ondrop" snippet into new items to give an idea of how to use it. While some of the other included test
data shows more intricate usage - for example an implemented magic misile spell and a health potion.

The following objects are provided:
player: the Character object that used the item. All events.
self: A refference back to the Item object of this particular one. All events.
target: the Character object the spell is used against. Only for events which have a target.
campaign: This is the campaign object currently loaded, you can use campaign.message(), campaign.warning()
    and campaign.error() to send messages from your spells to the screen.




