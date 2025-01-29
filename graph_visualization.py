import ipywidgets as widgets
from IPython.display import display, SVG
from graphviz import Digraph

# Definição da tabela de capacidades com base na planilha fornecida
capabilities_table = {
    "IDR": {
        "Audit/Compliance": ["Audit"],
        "DA account": ["Registers DA as a member"],
        "OM": ["Governs ecosystem data monetization rules"],
        "Certificates": ["Governs ecosystem data ownership rules"],
        "Payments": ["Governs VSS"],
        "DL": ["Governs ecosystem DL rules"]
    },
    "IDSF": {
        "Audit/Compliance": ["Audit"],
        "DA account": ["Authorizes DA as DSP operator"],
        "OM": ["Governs Offers System"],
        "DSP": ["Governs DSP system"]
    },
    "DW": {
        "Audit/Compliance": ["Supports audit"],
        "DA account": ["Onboards & Hosts DA"],
        "OM": ["Hosts OM"],
        "Certificates": ["Hosts certificates"],
        "DSP": ["Hosts DSP"],
        "PDW": ["Hosts PDwallets"],
        "Payments": ["Manages payments"],
        "BDW": ["Hosts bdwallets"],
        "VSS": ["Hosts VSS"],
        "DL": ["Hosts DL"]
    },
    "DA": {
        "Audit/Compliance": ["Receives Financial Reports"],
        "DA account": ["Manages own profile and account"],
        "OM": ["Manages Data Monetization Offers"],
        "Certificates": ["Manages DUC"],
        "DSP": ["Registers CDSP"],
        "PDW": ["Onboards PDwallets"],
        "Payments": ["Receives benefits"],
        "BDW": ["Onboards bdwallets"],
        "DL": ["Manages BRDs"]
    },
    "BDW": {
        "Audit/Compliance": ["Receives Financial Reports"],
        "OM": ["Creates and manages offers"],
        "Certificates": ["Signs certificates and manages portfolio"],
        "Payments": ["Pay for data monetization offer and receives benefits"],
        "DA account": ["Chooses DA and manages account"],
        "VSS": ["Registers and manages products"],
        "DL": ["Hosts and manages data monetization lake"]
    },
    "PDW": {
        "Audit/Compliance": ["Receives Financial Reports"],
        "OM": ["Receives and manages offers"],
        "Certificates": ["Signs certificates and manages portfolio"],
        "DSP": ["Chooses DSP and manages contributions"],
        "DA account": ["Chooses DA and manages account"],
        "Payments": ["Receives data benefits"]
    }
}

# Mapeamento de camadas por entidade
layers_mapping = {
    "IDR": ["Foundational"],
    "IDSF": ["Foundational"],
    "DW": ["Transactional"],
    "DA": ["Operational"],
    "BDW": ["Operational"],
    "PDW": ["Operational"]
}

# Captura todas as capabilities únicas presentes no dicionário
all_capabilities = sorted(set(cap for entity in capabilities_table.values() for cap in entity.keys()))

# Dropdowns de seleção corrigidos
capability_selector = widgets.Dropdown(
    options=all_capabilities, description="Capability:"
)
entity_selector = widgets.Dropdown(options=[""] + list(capabilities_table.keys()), description="Entity:")
layer_selector = widgets.Dropdown(options=[""], description="Layer:")
action_type_selector = widgets.RadioButtons(
    options=["Visualize Rule", "Visualize Cascade"], description="Action Type:"
)
execute_button = widgets.Button(description="Execute Action")
output = widgets.Output()

# Atualiza as opções do dropdown de layer com base na entidade selecionada
def update_layer_selector(change):
    entity = entity_selector.value
    layer_selector.options = layers_mapping.get(entity, [""])

entity_selector.observe(update_layer_selector, names="value")

# Visualizar uma regra específica por capability e entidade
def visualize_rule(capability, entity, layer):
    graph = Digraph(format="svg")

    if entity in capabilities_table and capability in capabilities_table[entity]:
        if layers_mapping.get(entity) and layer in layers_mapping[entity]:
            action = capabilities_table[entity][capability][0]
            label = f"{entity}\n{action}\n({layer})"
            graph.node(entity, label=label, shape="box")

    return graph

# Visualizar cascata completa por capability
def visualize_cascade(capability):
    graph = Digraph(format="svg", engine="dot")

    foundational = []
    transactional = []
    operational = []

    for entity, layer_list in layers_mapping.items():
        if capability in capabilities_table.get(entity, {}):
            action = capabilities_table[entity][capability][0]
            for layer in layer_list:
                label = f"{entity}\n{action}\n({layer})"
                graph.node(entity, label=label, shape="box")

                if layer == "Foundational":
                    foundational.append(entity)
                elif layer == "Transactional":
                    transactional.append(entity)
                else:
                    operational.append(entity)

    # Conectar entidades Foundational com <-> entre si
    for i in range(len(foundational)):
        for j in range(i + 1, len(foundational)):
            graph.edge(foundational[i], foundational[j], dir="both", constraint="false")

    # Conectar camadas abaixo
    if foundational and transactional:
        for f in foundational:
            for t in transactional:
                graph.edge(f, t, constraint="true")

    if transactional and operational:
        for t in transactional:
            for o in operational:
                graph.edge(t, o, constraint="true")

    if foundational and operational:
        for f in foundational:
            for o in operational:
                graph.edge(f, o, constraint="true")

    return graph

# Executa a ação selecionada (Visualize Rule ou Visualize Cascade)
def on_execute_action(b):
    with output:
        output.clear_output()
        capability = capability_selector.value
        entity = entity_selector.value
        layer = layer_selector.value
        action_type = action_type_selector.value

        if not capability:
            print("Selecione uma capability.")
            return

        if action_type == "Visualize Rule":
            if not entity:
                print("Selecione uma entidade para visualizar a regra.")
                return
            if not layer:
                print("Selecione um layer para visualizar a regra.")
                return
            graph = visualize_rule(capability, entity, layer)
            file_path = "/tmp/rule_graph"
            graph.render(file_path, cleanup=True)
            display(SVG(file_path + ".svg"))

            # Exibe os textareas de Modular Clauses
            modular_clause_1 = widgets.Textarea(
                value="**§1** The naming and descriptions of attributes in a Standard Value Schema must be clear, consistent, and descriptive, reflecting the content and purpose of the data.\nExample: Attributes should be named to avoid ambiguity, such as using 'City Name' instead of 'City' to ensure that the purpose of the attribute is easily understood by all users.",
                description="Standard VSS clauses",
                disabled=True,
                layout=widgets.Layout(width="100%", height="200px")
            )
            modular_clause_2 = widgets.Textarea(
                value="Assumption: The registration fee must be consistent across all registrations and must comply with local tax regulations.",
                description="Registration fee",
                disabled=True,
                layout=widgets.Layout(width="100%", height="100px")
            )

            display(modular_clause_1, modular_clause_2)

        elif action_type == "Visualize Cascade":
            graph = visualize_cascade(capability)
            file_path = "/tmp/cascade_graph"
            graph.render(file_path, cleanup=True)
            display(SVG(file_path + ".svg"))

# Bind do botão
execute_button.on_click(on_execute_action)

# Layout
widgets_box = widgets.VBox([
    capability_selector,
    entity_selector,
    layer_selector,
    action_type_selector,
    execute_button
])

display(widgets_box, output)
