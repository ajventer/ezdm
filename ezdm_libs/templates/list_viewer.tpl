<table border=1>
	<tr><td bgcolor=lightgray><strong>View {{name}}</strong></td></tr>
    <tr><td bgcolor=lightblue>
<ul>
{%- for item in list|sort %}                       
  <li>{{ item }}</li>                                                                     
{%- endfor %}   
</ul>
</td></tr></table>