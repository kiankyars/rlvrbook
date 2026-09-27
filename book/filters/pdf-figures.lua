-- PDF-only figure rules. Registered under format: pdf in _quarto.yml; the
-- FORMAT check keeps it inert if it is ever run for another format.
--
-- 1. Loads includes/pdf-figures.tex into the LaTeX preamble (size cap and
--    float placement for every figure).
-- 2. Gives a captioned image without a #fig- id, such as an Escher chapter
--    opener, an unnumbered caption, as in the HTML output, so it does not
--    use up a figure number and shift the numbers of real figures.

if not FORMAT:match("latex") then
  return {}
end

return {
  {
    Meta = function(meta)
      quarto.doc.include_file("in-header", "../includes/pdf-figures.tex")
      return meta
    end,

    Figure = function(fig)
      if fig.identifier == "" and #fig.caption.long > 0 then
        fig.attributes["quarto-caption-env"] = "caption*"
        return fig
      end
    end,
  },
}
