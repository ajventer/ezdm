<form action="/action{{action}}" method='post'>
<table border=1>
    <tr>
        <td bgcolor=lightgray>
            <center>{{name}}</center>
        </td>
    </tr>
    <td>{{question}}:
    <input type=text name="{{inputname}}" value="{{default_value}}">
</td>
</tr>
<tr>
    <td colspan=2>
        <center><input type=submit name="{{submitname}}" value="{{submitvalue}}"></center>
    </td>
</tr>
</table>
</form>