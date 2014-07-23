<table border=1 width=100%>
    <tr>
        {%for item in menuitems %}
        <td bgcolor=lightgray>
            <a href="/action/{{item}}">{{item}}</a>
        </td>
        {%endfor%}
        <td bgcolor=lightgray>
            <a href='/reset'>Reset sessions</a>
        </td>
    </tr>
</table>

