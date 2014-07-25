<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8">
	<title></title>
	<meta name="generator" content="LibreOffice 4.2.4.2 (Linux)">
	<meta name="created" content="20140725;0">
	<meta name="changed" content="20140725;35358574118851">
	<style type="text/css">
	<!--
		@page { margin: 2cm }
		p { margin-bottom: 0.25cm; line-height: 120% }
	-->
	</style>
</head>
<body lang="en-ZA" dir="ltr" style="background: transparent">
<p style="margin-bottom: 0cm; line-height: 100%">EZDM is a
free/open-source toolkit for dungeons and dragons dungeon-masters 
</p>
<p style="margin-bottom: 0cm; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0cm; line-height: 100%">Version 2.0 is a
near-complete rewrite of the original code with massive improvements
and much 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">higher code quality
in a truly elegant design.  EZDM encapsulates virtually all of the
ADnD2E ruleset in json data files, and could be adapted for other
editions or different gaming systems with relative ease as nearly all
the changes will be in the data files only (you would need to create
child-class of Character and override some methods however as these
are based on interpreting the 2E specific data). The system is based 
on python combined with json for data and jinja2 as the templating
engine for the web-based gui. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0cm; line-height: 100%">Usage: start the
ezdm server and point your browser to: http://localhost:8000 
</p>
<p style="margin-bottom: 0cm; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0cm; line-height: 100%">The library and data
system could, with relative ease be adapted to become the engine for
an RPG 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">game, either using
party or single-player mode but some functionality would have to be
added. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">I would like to do
so at some point.  As of version 2.0 the system has two distinct
modes of operation, which you can swith between at will.  In Dungeon
Master mode, you get the capacity to edit the data files for your
personal campaigns by hand. You would use this to initially created
character sheets for players, design maps or  create spells and
items. In Campaign mode the tools behave more like a game, displaying
the (revealed parts of the) map and activities based on that or, when
needed, the combat engine. All of this is turn-based in true DND
style. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">As a dungeon master
preparing for a session you will likely switch between these modes
frequently as you access various tools to prepare (and test) portions
of the campaign. The system ships with some sample data, while any
you add are saved in your home directory. EZDM is not a complete
replacement for your normal DM role nor is it intended to be, it's
job is merely to let you focus on story-telling while doing the hard
maths for you. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%"><br>
</p>
<p style="margin-bottom: 0cm; line-height: 100%"><br>
</p>
<ul>
	<li><p style="margin-bottom: 0cm; line-height: 100%">Included tools:
		</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Dungeon Master
	mode: 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Character
	Sheet editor (for players and monsters) 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Item Editor 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Map Editor 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">Campaign Mode: 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Map
	Viewer/Navigator (hiding unrevealed parts) - behaves much like
	roguelikes do. 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Dice Roller
	(for when you need to roll on something storywise that isn't coded
	into the map) 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Combat Engine
	(choose who is in, EZDM will handle initiative rolls and the fight
	details based on player choices). 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Character
	sheet view. 
	</p>
	<li><p style="margin-bottom: 0cm; line-height: 100%">	Inventory
	management. 
	</p>
</ul>
<p style="margin-bottom: 0cm; line-height: 100%">Magic: 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">Perhaps the hardest
part to implement in EZDM was magic, in all it's sources. EZDM
handles this in a very elegant manner however. All items can,
potentially, have magical effects - and spells are just a type of
Item which is kept in a special inventory slot. The json files
holding the data for items have a section called &quot;events&quot;. 
Within this are subkeys for various supported events. Within these
subkeys you implement magic by writing  short python snippets. The
snippets run in a tightly constrained environment, but depending on
the event have access to the objects they need to manipulate in order
to function. The item template automatically inserts a small sample 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">&quot;ondrop&quot;
snippet into new items to give an idea of how to use it. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">The following
objects are provided: 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">player: the
Character object that used the item. All events. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">self: A refference
back to the Item object of this particular one. All events. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">target: the
Character object the spell is used against. Only for events which
have a target. 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">page: the Page
object for the next render of the screen, by using it's methods you
can put messages 
</p>
<p style="margin-bottom: 0cm; line-height: 100%">on the screen,
communicating your spell's effects to the user. All events. 
</p>
</body>
</html>