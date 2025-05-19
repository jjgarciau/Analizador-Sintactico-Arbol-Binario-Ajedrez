import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsLineItem
)
from PyQt6.QtGui import QBrush, QPen
from PyQt6.QtCore import Qt

# Nodo para el árbol binario (turno)
class TreeNode:
    def __init__(self, move):
        self.move = move
        self.left = None  # nodo izquierdo: movimiento blanco
        self.right = None  # nodo derecho: movimiento negro

# Clase para la ventana principal
class ChessSANValidator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validador y Árbol Binario de Partida de Ajedrez (SAN)")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "Ingrese la partida en notación SAN (ejemplo: 1. e4 e5 2. Nf3 Nc6 ...)"
        )
        self.layout.addWidget(self.input_text)

        self.validate_btn = QPushButton("Validar y Mostrar Árbol")
        self.validate_btn.clicked.connect(self.validate_and_show_tree)
        self.layout.addWidget(self.validate_btn)

        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.layout.addWidget(self.graphics_view)
        self.root = None

    def validate_and_show_tree(self):
        san_text = self.input_text.toPlainText().strip()
        if not san_text:
            QMessageBox.warning(self, "Error", "Por favor, ingrese una partida.")
            return

        try:
            moves = self.parse_san(san_text)
        except ValueError as e:
            QMessageBox.critical(self, "Error de validación", str(e))
            return

        self.build_tree(moves)
        self.draw_tree()

    def parse_san(self, san_text):
        # Regex simplificado para detectar turnos (número + . + movimientos)
        # Se separa en movivimientos para analizar
        turnos = re.split(r'\d+\.', san_text)
        turnos.pop(0)
        moves = []

        i = 0
        while i < len(turnos):

            turno = turnos[i].strip()
            turno = turno.split()

            if len(turno) > 2:
                # Si hay más de 2 caracteres, es un error
                raise ValueError(f"Error: No puede haber más de dos movimientos por turno en '{turno}'")
            
            white_move = turno[0]
            if not self.is_valid_move(white_move):
                raise ValueError(f"Movimiento blanco inválido en turno {i + 1}: {white_move}")

            black_move = turno[1] if len(turno) > 1 else None
            if black_move != None and not self.is_valid_move(black_move):
                raise ValueError(f"Movimiento negro inválido en turno {i + 1}: {black_move}")
            i += 1 
            
            # Insertamos turno[0] y turno[1]
            moves.append(turno[0])
            if len(turno) > 1:
                moves.append(turno[1])
            

        return moves

    def is_valid_move(self, move):
        # Validación basada en la BNF simplificada y ejemplos
        # Movimientos permitidos:
        # Enroques: O-O, O-O-O
        # Movimiento pieza: [KQRBN][a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?[+#]?
        # Movimiento peón: ([a-h]x)?[a-h][1-8](=[QRBN])?[+#]?

        # Patron para enroque
        if move in ("O-O", "O-O-O"):
            return True

        piece = "[KQRBN]"
        column = "[a-h]"
        row = "[1-8]"
        promotion = "(=[QRBN])?"
        checkmate = "[+#]?"

        # Movimiento pieza con posible desambiguación y captura
        pattern_piece = rf"^{piece}({column}|{row}|{column}{row})?x?{column}{row}{promotion}{checkmate}$"
        # Movimiento peón captura
        pattern_pawn_capture = rf"^{column}x{column}{row}{promotion}{checkmate}$"
        # Movimiento peón avance normal
        pattern_pawn_move = rf"^{column}{row}{promotion}{checkmate}$"

        if re.match(pattern_piece, move):
            return True
        if re.match(pattern_pawn_capture, move):
            return True
        if re.match(pattern_pawn_move, move):
            return True

        return False
    
    def insert(self, move):
        new_node = TreeNode(move)
        
        queue = [self.root]
        while queue:
            current_node = queue.pop(0)
            
            if not current_node.left:
                current_node.left = new_node
                return
            else:
                queue.append(current_node.left)
            
            if not current_node.right:
                current_node.right = new_node
                return
            else:
                queue.append(current_node.right)


    def build_tree(self, moves):
        self.root = TreeNode("Partida")

        for move in moves:
            self.insert(move)
        
    def draw_tree(self):
        self.scene.clear()
        if self.root is None:
            return

        node_radius = 20
        y_start = 40         
        level_gap_y = 55     
        x_spacing = 6        

        # Primer recorrido: asigna posición x a cada nodo (in-order)
        positions = {}
        def assign_positions(node, depth=0):
            # Usa una variable mutable para llevar la cuenta de la posición x global
            nonlocal_counter = assign_positions.counter
            if node.left: 
                assign_positions(node.left, depth+1)
            positions[node] = (nonlocal_counter[0], depth)
            nonlocal_counter[0] += 1
            if node.right:
                assign_positions(node.right, depth+1)
        assign_positions.counter = [0]
        assign_positions(self.root)

        print(positions.values())
        # Segundo recorrido: dibuja usando las posiciones calculadas
        def draw_node(node, is_right_child=False):
            if node is None:
                return
            x_idx, depth = positions[node]
            x = 50 + x_idx * (node_radius * 2 + x_spacing)
            y = y_start + depth * level_gap_y

            # Colorear el nodo según si es hijo derecho o no
            ellipse = QGraphicsEllipseItem(x, y, node_radius*2, node_radius*2)
            if is_right_child:
                ellipse.setBrush(QBrush(Qt.GlobalColor.black))
            else:
                ellipse.setBrush(QBrush(Qt.GlobalColor.white))
            ellipse.setPen(QPen(Qt.GlobalColor.black))
            self.scene.addItem(ellipse)

            # Creamos el texto del nodo
            text_item = QGraphicsTextItem(node.move)

            # Centramos el texto en el nodo
            text_rect = text_item.boundingRect()
            text_x = x + node_radius - text_rect.width() / 2
            text_y = y + node_radius - text_rect.height() / 2
            text_item.setPos(text_x, text_y)

            # Cambiar el color del texto según el color del nodo
            if is_right_child:
                text_item.setDefaultTextColor(Qt.GlobalColor.white)
            else:
                text_item.setDefaultTextColor(Qt.GlobalColor.black)
            self.scene.addItem(text_item)

            # Draw lines to children
            if node.left:
                child_x_idx, child_depth = positions[node.left]
                child_x = 50 + child_x_idx * (node_radius * 2 + x_spacing)
                child_y = y_start + child_depth * level_gap_y
                line = QGraphicsLineItem(
                    x + node_radius, y + node_radius*2,
                    child_x + node_radius, child_y
                )
                self.scene.addItem(line)
                draw_node(node.left, is_right_child=False)  # Hijo izquierdo: blanco

            if node.right:
                child_x_idx, child_depth = positions[node.right]
                child_x = 50 + child_x_idx * (node_radius * 2 + x_spacing)
                child_y = y_start + child_depth * level_gap_y
                line = QGraphicsLineItem(
                    x + node_radius, y + node_radius*2,
                    child_x + node_radius, child_y
                )
                self.scene.addItem(line)
                draw_node(node.right, is_right_child=True)  # Hijo derecho: negro

        draw_node(self.root)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessSANValidator()
    window.show()
    sys.exit(app.exec())
