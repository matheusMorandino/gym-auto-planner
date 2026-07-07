import json
from pathlib import Path


def read_json(path: str) -> dict:
    """
    Read a json file
    :param path: path to json file
    :return: JSON data
    """
    with open(path, 'r') as f:
        return json.load(f)


def load_svg(path: str):
    svg = Path(path).read_text()

    js = """
    <script>
    const selected = new Set();

    function toggle(id){
        const g = document.getElementById(id);

        if(selected.has(id)){
            selected.delete(id);

            g.querySelectorAll("path,polygon").forEach(e=>{
                e.style.fill="";
            });
        }else{
            selected.add(id);

            g.querySelectorAll("path,polygon").forEach(e=>{
                e.style.fill="#ff4444";
            });
        }

        window.dispatchEvent(
            new CustomEvent(
                "muscle-selection",
                {detail:Array.from(selected)}
            )
        );
    }

    document.querySelectorAll("g[id]").forEach(g=>{
        g.style.cursor="pointer";
        g.onclick=()=>toggle(g.id);
    });
    </script>
    """

    return svg.replace("</svg>", js + "</svg>")
