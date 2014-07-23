<table border=1 width=60%>
    <tr><td bgcolor=lightblue width=60%>
{% if json.icon %}
	<img align=right src="/icon/{{json.icon}}" border=0>
{% endif %}    	
<ul>
{%- for key, value in json.items() recursive %}                       
  <li>{{ key }}                                                           
    {%- if value is mapping %}                                                                                                
      <ul>{{ loop(value.items())}}</ul>
    {% else %}
        = {{value}}
    {%- endif %}                                                            
  </li>                                                                     
{%- endfor %}   
</ul>
</td>
</tr></table>