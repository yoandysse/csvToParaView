import pandas as pd
import sys
import vtk
import datetime

def read_csv(filename):
    # Leer los datos desde el nuevo archivo CSV
    data = pd.read_csv(filename, delimiter=",", header=0)

    return data

def calculate_dimension(data, column):
    # Calcular dimensions
    df_dimension = pd.DataFrame(columns=['first_change', 'dimension', 'eje'])

    for column in column:
        # encontrar el primer cambio
        first_change = data[data[column].shift(-1) != data[column]].index[0]
        # obtener el numero de valores unicos
        dimension = data[column].nunique()
        # agregar a df_dimension
        df_tmp = pd.DataFrame({'first_change': first_change, 'dimension': dimension, 'eje': column}, index=[0])
        df_dimension = pd.concat([df_dimension, df_tmp], ignore_index=True)

    df_dimension = df_dimension.sort_values(by=['first_change'])


    return df_dimension.iloc[0]['dimension'], df_dimension.iloc[1]['dimension'],df_dimension.iloc[2]['dimension']

def generate_vtk(input_file, output_filename=None, output_type=None):

    # Leer los datos desde el nuevo archivo CSV
    data = read_csv(input_file)


    # Crear estructura
    grid = vtk.vtkStructuredGrid()

    # Create puntos
    points = vtk.vtkPoints()

    # Agregar datos a los puntos
    for i in range(data.shape[0]):
        points.InsertNextPoint(data.iloc[i]['x'], data.iloc[i]['y'], data.iloc[i]['z'])

    grid.SetPoints(points)

    # Agregar dimensiones
    grid.SetDimensions(calculate_dimension(data, column=['x', 'y', 'z']))

    # Crear array de temperatura
    temperature = vtk.vtkFloatArray()
    temperature.SetName("Temperatura")

    # Agregar datos a temperatura
    for i in range(data.shape[0]):
        temperature.InsertNextValue(data.iloc[i]['Temperatura'])

    # Agregar array de temperatura al estructura
    grid.GetPointData().AddArray(temperature)

    # region Escribir la estructura a un archivo vtk
    writer = vtk.vtkStructuredGridWriter()

    if output_filename is None:
        output_filename = 'output.vtk'

    writer.SetFileName(output_filename)
    writer.SetInputData(grid)

    if output_type is None:
        output_type = 'binary'
    elif output_type == 'ascii':
        writer.SetFileTypeToASCII()
    elif output_type == 'binary':
        writer.SetFileTypeToBinary()

    writer.Write()
    # endregion Escribir la estructura a un archivo vtk


if __name__ == '__main__':

    if len(sys.argv) == 1:
        input_file = input("Introduce el nombre del dataset (default=data.csv): ")
        output_file = input("Introduce el nombre del archivo VTK de salida (opcional, por defecto output.vtk): ")
        output_type = input("Introduce el formato de salida del archivo [1]-binary (default) [2]-ascii: ")

        if input_file == '':
            input_file = 'data.csv'

        if output_file == '':
            output_file = None

        if output_type == '' or output_type == '1' or output_type == 'binary':
            output_type = 'binary'
        elif output_type == '2' or output_type == 'ascii':
            output_type = 'ascii'
        else:
            output_type = 'binary'

    start_time = datetime.datetime.now()

    print("Tiempo de inicio: {}".format(start_time.strftime("%H:%M:%S")))

    generate_vtk(input_file=input_file, output_filename='output.vtk', output_type=output_type)

    end_time = datetime.datetime.now()

    print("Tiempo de ejecución: {:.2f} minutos".format((end_time - start_time).total_seconds() / 60))
    print("Hora de finalización: {}".format(end_time.strftime("%H:%M:%S")))

