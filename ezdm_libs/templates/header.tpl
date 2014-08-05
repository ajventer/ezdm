<html>
<head>
    <title>{{title}}</title>
</head>
<body>
<center>
    <table width=100% cellpadding=10 cellspacing=0 border=1>
        <tr>
        	<td width=10% bgcolor=lightblue><strong><a href="/mode/campaign">Campaign</a></strong></td>
            <td bgcolor=lightblue width=50%><center><strong>{{title}}</strong></center>
            {% if character %}   
                </td><td bgcolor=lightblue align=left>Current character:
                    <img src="/icon/{{character.get('/core/icon','')}}" height=25>{{character.displayname()}}
                    <input type=button value="End Round" onclick="window.location = '/endround'">
            {% endif %}
            </td>
            <td width=10% bgcolor=lightblue><strong><a href="/mode/dm">Dungeon Master</a></strong></td>
        </tr>
    </table>
