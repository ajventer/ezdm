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
        <td bgcolor=lightblue colspan=3><strong><center>Spellbook</center></strong></spellbook>
    </tr>
    <tr>
        <td bgcolor=lightgray>Spell Book</td>
        <td bgcolor=lightgray>Spells Memorized</td>
        <td bgcolor=lightgray>Detail view</td>
    </tr>
    <tr>
        <td valign=top>
            <ul>
                {% for section,spell,index in spells %}
                <li>
                    <a href=# onclick="clickHandler('{{index}}','spellbook')">
                        {{spell.displayname()}} </a>
                    <img onclick="clickHandler('{{index}}','spellbook')" src="/icon/{{spell.get('/core/icon','')}}">
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
        <td valign=top>
            {% if spellprog %}
                {% set spelltype = spellprog.keys()[0] %}
                <form method=post>
                <fieldset>
                        <legend><strong>{{spelltype.upper()}}</strong></legend>
                        <div style="background-color: #ccffcc; border: 3px solid;">
                        {%for key in spellprog[spelltype] | sort %}
                            {% set ikey = key|int %}
                            <div style="background-color: #ccffcc; border: 3px solid; display: table-row;">
                               Level {{key}} spells:
                            {% set count = 0 %}
                            {% for spell in memorized[ikey] %}
                                {% set count = count + 1 %}
                                <div  style="background-color: #ccffcc; border: 2px solid; display: table-cell;">
                                {% set spellview = spells[spell] %}
                                  <a href=# onclick="clickHandler('{{spell}}','memory')">
                                    {{spellview[1].displayname()}}</a>
                                  <img  onclick="clickHandler('{{spell}}','memory')" src="/icon/{{spellview[1].get('/core/icon','')}}">
                                </div>
                            {% endfor %}
                            {% set available = spellprog[spelltype][key] - count %}    
                            {% for count in range(0,available) %}
                            <div  style="background-color: #ccffcc; border: 2px solid; display: table-cell;">
                                    <select name="memorize_spell">
                                        <option value="ignoreme"></option>
                                        {% for section,spell,index in spells %}
                                            {% set level = spell.get('/conditional/spell_level',1)|string %}
                                            {% if level == key %}
                                                <option value="{{index}}">{{spell.displayname()}}</option>
                                            {% endif %}
                                        {% endfor %}
                                    </select>
                            </div>

                            {% endfor %} 
                            </div>   
                        {% endfor %}
                        <input type=submit value="Memorize Spells" name="memorize_spells">
                    </div>
               </fieldset> 
                </form>
            {% endif %}
        </td>
        <td valign=top>
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
                <form method=post>              
                    {% if editmode %}
                            <input type=hidden name="spellindex" value="{{detailidx}}">
                            <input type=hidden name="spellsection" value="{{detailsection}}">
                            <input type=submit name="unlearn" value="Unlearn Spell">
                    {% endif %}
                    {% if not editmode %}
                        <input type=hidden name="pack_index" value="{{detailidx}}">
                        {% if detailsection == 'memory' %}
                            <select name="cast_spell_target">
                                {% for target in targetlist %}
                                    <option value="{{target.name()}}">{{target.displayname()}}</option>
                                {% endfor %}
                            </select>
                                <input type=submit name="cast_spell" value="Cast spell">                    
                            {% endif %}
                            {% if detailview.get('/core/in_use', false) %}
                                <input type=submit name="stopcasting" value="Stop casting">
                            {% endif %}
                        {% endif %}
                    </form>
                    {% endif %}

        </td>
    </tr>

</table>