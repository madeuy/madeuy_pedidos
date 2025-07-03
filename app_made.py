import streamlit as st
import pandas as pd
from io import BytesIO
import yagmail
import os

# --- Títulos y formulario cliente ---
st.title("Formulario de Pedido de Remeras")

st.subheader("Datos del cliente")
nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
medio = st.selectbox("Medio de contacto", ["Instagram", "WhatsApp", "Otro"])
usuario = st.text_input("Usuario o teléfono")
mail = st.text_input("Correo electrónico")

# --- Selección de talles ---
st.subheader("Cantidad por talle")
talles_textiles = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
talles_numericos = [str(i) for i in range(0, 18, 2)]
todos_talles = talles_textiles + talles_numericos

talles_cantidad = {}
cols = st.columns(6)
for i, talle in enumerate(todos_talles):
    with cols[i % 6]:
        cantidad = st.number_input(f"{talle}", min_value=0, max_value=20, step=1)
        if cantidad > 0:
            talles_cantidad[talle] = cantidad

# --- Mostrar segundo formulario solo si hay talles ---
campos_formulario_2 = []
if talles_cantidad:
    st.subheader("Detalle por prenda")

    for talle, cantidad in talles_cantidad.items():
        for i in range(cantidad):
            st.markdown(f"**Talle {talle} – Prenda {i+1}**")
            col1, col2 = st.columns([2, 3])
            with col1:
                persona = st.text_input(f"¿Para quién es? (Talle {talle}, prenda {i+1})", key=f"persona_{talle}_{i}")
            with col2:
                ubicacion = st.multiselect(
                    "Ubicación de estampa",
                    ["pecho", "espalda", "manga"],
                    key=f"ubicacion_{talle}_{i}"
                )
            campos_formulario_2.append((talle, persona, ubicacion))

# --- Botón para enviar ---
if campos_formulario_2 and st.button("Enviar pedido"):
    errores = []
    datos = []

    for i, (talle, persona, ubicacion) in enumerate(campos_formulario_2, 1):
        if not persona.strip() or not ubicacion:
            errores.append(f"Fila {i}: faltan datos (Nombre o ubicación)")
        datos.append({
            "Talle": talle,
            "Persona": persona.strip(),
            "Ubicación": ", ".join(ubicacion)
        })

    if errores:
        st.error("No se puede enviar el pedido. Corregí los siguientes errores:")
        for e in errores:
            st.write(f"- {e}")
    else:
        df_pedido = pd.DataFrame(datos)
        df_cliente = pd.DataFrame([{
            "Nombre": nombre.strip(),
            "Apellido": apellido.strip(),
            "Medio": medio,
            "Usuario": usuario.strip(),
            "Mail": mail.strip()
        }])

        conteo_por_talle = df_pedido["Talle"].value_counts().sort_index()
        df_resumen = conteo_por_talle.reset_index()
        df_resumen.columns = ["Talle", "Cantidad"]
        total = pd.DataFrame([{"Talle": "TOTAL", "Cantidad": df_resumen["Cantidad"].sum()}])
        df_resumen = pd.concat([df_resumen, total], ignore_index=True)

        # Guardar Excel en archivo físico
        nombre_archivo = "pedido_personalizado.xlsx"
        with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
            df_cliente.to_excel(writer, sheet_name="datos_cliente", index=False)
            df_resumen.to_excel(writer, sheet_name="resumen_pedido", index=False)
            df_pedido.to_excel(writer, sheet_name="datos_pedido", index=False)

        # Enviar correo
        try:
            st.info("Enviando archivo por correo a gqq@gmail.com...")

            remitente = "madeformulario@gmail.com"  
            clave = "byeatdzpupzqlyec"       

            yag = yagmail.SMTP(user=remitente, password=clave)
            yag.send(
                to="gqq@gmail.com",
                subject="Nuevo pedido de remeras",
                contents="Se adjunta el archivo con los datos del pedido.",
                attachments=nombre_archivo
            )

            st.success("📧 Pedido enviado correctamente a gqq@gmail.com")

            os.remove(nombre_archivo)  # Limpieza del archivo temporal

        except Exception as e:
            st.error(f"Error al enviar el correo: {e}")


            st.success("📧 Correo enviado correctamente a gqq@gmail.com")

        except Exception as e:
            st.error(f"Error al enviar el correo: {e}")
