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
            <td>{{combatgrid[c][e]}}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>