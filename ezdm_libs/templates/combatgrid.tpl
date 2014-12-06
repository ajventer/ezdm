Rows: Attackers<br>
Columns: Targets<br>
<table border=5>
    <tr>
        <td></td>
        {% for c in combatgrid.keys() | sort %}
            <td bgcolor=lightgray>{{c}}</td>
        {% endfor %}
    </tr>
    {% for c in combatgrid.keys() | sort %}
    <tr>
        <td bgcolor=lightgray>{{c}}</td>
        {% for e in combatgrid[c].keys() | sort %}
        {% set roll = combatgrid[c][e] %}
        {% if roll > 20 %}
            <td bgcolor=red>
        {% else %}
            <td>
        {% endif %}
            {{roll}}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table><br>
<strong>Modifiers:</strong>
<table border=1>
    {% for mod in mods %}
        <tr>
            <td bgcolor=lightgray>{{mod}}</td>
            <td>{{mods[mod]}}</td>
        </tr>
    {% endfor %}
</table>