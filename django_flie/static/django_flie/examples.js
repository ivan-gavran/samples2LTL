function example1 () {
  ace.edit("id_editor").setValue("{\n\"literals\":[\"p\", \"q\", \"r\"],\"positive\":\n  [\n    \"p,q; p; null| p\",\n    \"null; q; null| p\"\n  ],\n\"negative\":\n  [\n    \"r; p; null| p\"\n  ],\n\"number-of-formulas\": 3,\n\"max-depth-of-formula\": 4,\n\"operators\":[\"F\", \"->\", \"&\", \"|\", \"U\", \"G\", \"X\"]\n}", 1);
}

function example2 () {
  ace.edit("id_editor").setValue("{\n\"literals\":[\"p\", \"q\", \"r\"],\n\"positive\":\n  [\n    \"p,q; p; null| p\",\n    \"p; null; ; | p; q\"\n  ],\n\"negative\":\n  [\n    \"; p; null| p\",\n    \"null; null; ; | p; q\"\n  ],\n\"number-of-formulas\": 3\n}", 1);
}

function example3 () {
  ace.edit("id_editor").setValue("{\n\"literals\": [\"p\", \"q\", \"r\"],\n\"positive\":\n  [\n    \"p,q; p; null| p\",\n    \"null; q; null| p\"\n  ],\n\"negative\":\n  [\n    \"; p; null| p\"\n  ],\n\"number-of-formulas\": 3\n}", 1);
}
