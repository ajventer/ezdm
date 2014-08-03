<table border=1 width=100%>
    <tr>
        {%for key in menuitems |sort %}
        <td bgcolor=lightgray>
            <a href="/action/{{key}}">{{menuitems[key]}}</a>
        </td>
        {%endfor%}
    </tr>
</table>

