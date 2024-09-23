# Physics Data Generator Extension for NVIDIA Omniverse

This project implements a Physics Data Generator extension for NVIDIA Omniverse. It's designed to generate physics simulation data that can be used for training AI models. The extension is currently in early testing, with the goal of producing data similar to that used in projects like AISand for physics prediction.

## Features (Early Testing)

- Custom UI in Omniverse with progress tracking
- Asynchronous data generation to maintain UI responsiveness
- Random scenario generation with various primitive types (Sphere, Cube, Cylinder)
- Physics simulation using Omniverse's physics engine
- JSON output of simulation data including object positions and rotations over time

## Requirements

- NVIDIA Omniverse Kit
- Python 3.7+

## Installation

1. Clone this repository into your Omniverse extension directory:
   ```
   git clone https://github.com/your-username/physics-data-generator.git
   ```
2. Ensure the extension directory structure is as follows:
   ```
   omniverse/exts/com.example.physics_data_generator/
   ├── config/
   │   └── extension.toml
   └── physics_data_generator/
       ├── __init__.py
       ├── extension.py
       └── data_generator.py
   ```

## Usage

1. Launch NVIDIA Omniverse
2. Enable the Physics Data Generator extension in the Extension Manager
3. Click the "Generate Data" button to start the data generation process
4. Monitor progress in the UI
5. Once complete, find the generated data in the `physics_data.json` file

## Data Output

The generated data is saved in JSON format with the following structure:
```json
[
  {
    "scenario_id": "unique_id",
    "timesteps": [
      {
        "time": 0.0,
        "objects": [
          {
            "id": "object_id",
            "type": "sphere",
            "position": [x, y, z],
            "rotation": [qw, qx, qy, qz]
          },
          ...
        ]
      },
      ...
    ]
  },
  ...
]
```

## Future Goals

The aim is to generate physics simulation data that can be used to train AI models for physics prediction, similar to the AISand project. Future developments may include:

- More diverse scenario generation
- Additional physics properties (velocity, acceleration, etc.)
- Integration with machine learning pipelines
- Real-time visualization of generated scenarios

## License

This project is licensed under the GPL3
2024 David Hamner

## Acknowledgments

- NVIDIA Omniverse team for the platform and SDK
- Inspiration drawn from projects like AISand for physics prediction
- Claude ai for coding assistance. 


