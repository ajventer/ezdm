<table border=1>
    <tr><td bgcolor=lightblue>
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
</td></tr></table>