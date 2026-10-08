function Code(el)
  local ascii = {['→']='->',['←']='<-',['π']='pi',['φ']='phi',
    ['ψ']='psi',['ω']='omega',['β']='beta',['Ω']='ohm',['Σ']='Sigma',
    ['Δ']='Delta',['≈']='approximately',['≤']='<=',['≥']='>=',
    ['×']='*',['±']='+/-',['²']='^2',['“']='"',['”']='"'}
  for k,v in pairs(ascii) do el.text=el.text:gsub(k,v) end
  if #el.text > 18 then
    -- Paths and long identifiers need legal line breaks in the printed report.
    local s = el.text:gsub("|", "/")
    return pandoc.RawInline('latex', '\\path|' .. s .. '|')
  end
  return el
end

function Str(el)
  local symbols={['π']='\\pi',['β']='\\beta',['Δ']='\\Delta',
    ['Ω']='\\Omega',['Σ']='\\Sigma',['²']='{}^2',['×']='\\times',
    ['±']='\\pm',['≈']='\\approx',['≤']='\\leq',['→']='\\rightarrow'}
  local out,buf={},''
  for _,c in utf8.codes(el.text) do
    local char=utf8.char(c)
    if symbols[char] then
      if #buf>0 then table.insert(out,pandoc.Str(buf));buf='' end
      table.insert(out,pandoc.Math('InlineMath',symbols[char]))
    else buf=buf..char end
  end
  if #buf>0 then table.insert(out,pandoc.Str(buf)) end
  return out
end

function Image(el)
  el.src = el.src:gsub('%.svg$', '.pdf')
  return el
end

function Header(el)
  local title=pandoc.utils.stringify(el.content)
  if title == 'GESC Gaussian V3 Complete Project and Learning Report' then
    return {}
  end
  local start_page={['What this report establishes']=true}
  if el.level == 1 and start_page[title] then
    return {pandoc.RawBlock('latex','\\clearpage'),el}
  end
  return el
end
