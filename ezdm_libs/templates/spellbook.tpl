<form id="clickform" method=post>
    <input type=hidden id="selected" name="selected" value="">
    <input type=hidden name="section" id="section" value="">
</form> 
<script>
    function clickHandler(selected,section) {
        document.getElementById('selected').value = selected;
        document.getElementById('section').value = section;
        document.getElementById('clickform').submit();
    }
</script>
<table witdh=100% border=1>
    <tr>
        <td bgcolor=lightblue colspan=2><strong><center>Spellbook</center></strong></spellbook>
    </tr>
    <tr>
        <td bgcolor=lightgray>Spell List</td><td bgcolor=lightgray>Detail view</td>
    </tr>
    <tr>
        <td>
            <ul>
                {% for section,spell,index in spells %}
                <li>
                    {{spell.displayname()}} <img onclick="clickHandler('{{index}}','{{section}}')" src="/icon/{{spell.get('/core/icon','')}}">
                </li>
                {% endfor %}
            </ul><br>
            {% if editmode %}
            <form method=post>
                <select name="learnspell">
                    {% for spell in spell_list %}
                        <option value="{{spell}}">{{spell}}
                    {% endfor %}
                </select>
                <input type=submit value="Learn spell">
            </form>
            {% endif %}
        </td>
        <td>
            {% if detailview %}
                <ul>
                {%- for key, value in detailview.items() recursive %}                       
                  <li>{{ key }}                                                           
                    {%- if value is mapping %}                                                                                                
                      <ul>{{ loop(value.items())}}</ul>
                    {% else %}
                        = {{value}}
                    {%- endif %}                                                            
                  </li>                                                                     
                {%- endfor %}   
                </ul>  
                <br>
                {% if editmode %}
                    <form method=post>
                        <input type=hidden name="spellindex" value="{{detailidx}}">
                        <input type=submit name="unlearn" value="Unlearn Spell">
                    </form>
                {% endif %}              
            {% endif %}

        </td>
    </tr>

</table>