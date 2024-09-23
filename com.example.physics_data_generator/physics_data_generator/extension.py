import omni.ext
import omni.ui as ui
from .data_generator import PhysicsDataGenerator
import asyncio
import carb

class PhysicsDataGeneratorExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        print("[com.example.physics_data_generator] PhysicsDataGenerator startup")
        self._window = ui.Window("Physics Data Generator", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Physics Data Generator")
                self._generate_button = ui.Button("Generate Data", clicked_fn=self.generate_data)
                self._progress_bar = ui.ProgressBar(height=20)
                self._progress_bar.visible = False
                self._status_label = ui.Label("")

    def on_shutdown(self):
        print("[com.example.physics_data_generator] PhysicsDataGenerator shutdown")

    def generate_data(self):
        self._generate_button.enabled = False
        self._progress_bar.visible = True
        self._status_label.text = "Data generation started. Please wait..."
        asyncio.ensure_future(self.async_generate_data())

    async def async_generate_data(self):
        try:
            generator = PhysicsDataGenerator()
            data = await generator.run_simulation(
                progress_callback=self.update_progress,
                status_callback=self.update_status
            )
            await generator.save_data(data)
            self._status_label.text = "Data generation complete. Saved to physics_data.json"
        except Exception as e:
            carb.log_error(f"Error during data generation: {str(e)}")
            self._status_label.text = f"Error: {str(e)}"
        finally:
            self._generate_button.enabled = True
            self._progress_bar.visible = False

    def update_progress(self, progress):
        self._progress_bar.model.set_value(progress)

    def update_status(self, status):
        self._status_label.text = status
