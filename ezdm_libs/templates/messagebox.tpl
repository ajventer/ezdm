<table border=5 bordercolor=darkgrey>
    <tr><td bgcolor=lightgray>
        {% for message in messages %}
            {{message}}<br>
        {% endfor %}
        {% for message in warnings %}
            <font color=orange>Warning:{{message}}</font><br>
        {% endfor %}
        {% for message in errors %}
            <font color=red>Warning:{{message}}</font><br>
        {% endfor %}
    </td>
</tr>
</table>